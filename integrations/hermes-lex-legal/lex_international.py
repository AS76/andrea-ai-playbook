#!/usr/bin/env python3
"""Bounded UK/NL official retrieval. No LLM, subscriptions or daemon."""
import argparse, datetime as dt, hashlib, json, pathlib, re, sys, time, fcntl
from urllib.parse import urlparse, urljoin, urlencode
import requests
from bs4 import BeautifulSoup
from defusedxml import ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
DATA=ROOT/"data"/"international"
HOSTS={"www.legislation.gov.uk","zoekservice.overheid.nl","repository.officiele-overheidspublicaties.nl","www.belastingdienst.nl"}
class SourceError(Exception): pass
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def norm(s): return " ".join(s.split())
def sha(b): return hashlib.sha256(b).hexdigest()
def date(s):
    v=dt.date.fromisoformat(s)
    if v>dt.datetime.now(dt.timezone.utc).date(): raise SourceError("future_date_not_supported")
    return v.isoformat()
def fetch(url):
    def allowed(u):
        p=urlparse(u)
        return p.scheme=="https" and p.hostname in HOSTS and p.port in (None,443) and not p.username and not p.password
    if not allowed(url): raise SourceError("source_not_allowed")
    DATA.mkdir(parents=True,exist_ok=True,mode=0o700)
    with (DATA/"network.lock").open("a+") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX); time.sleep(.3)
        try:
            for _ in range(5):
                r=requests.get(url,timeout=(5,20),stream=True,allow_redirects=False,headers={"User-Agent":"LexLegalResearch/0.2 (selective official research)","Accept":"application/xml,text/html"})
                if r.status_code in (301,302,303,307,308):
                    target=urljoin(url,r.headers.get("Location",""));r.close()
                    if not allowed(target):raise SourceError("redirect_not_allowed")
                    url=target;continue
                with r:
                    if r.status_code!=200:raise SourceError("source_http_"+str(r.status_code))
                    chunks=[];size=0
                    for b in r.iter_content(65536):
                        size+=len(b)
                        if size>8*1024*1024:raise SourceError("document_too_large")
                        chunks.append(b)
                    return b"".join(chunks),url
            raise SourceError("redirect_limit")
        except requests.RequestException as e:raise SourceError("source_unavailable_"+type(e).__name__) from None
def xml(raw):
    try:return ET.fromstring(raw)
    except Exception:raise SourceError("invalid_or_unsafe_xml") from None
def local(n):return n.tag.split("}")[-1]
def nodes(r,name):return [n for n in r.iter() if local(n)==name]
def val(r,name):
    ns=nodes(r,name);return norm(" ".join(ns[0].itertext())) if ns else None
def document(source,ident,locator,asof,text,raw,url,title,kind="norm"):
    return {"source_key":source,"official_id":ident,"locator":locator,"applicable_on":asof,
        "version_label":asof or now()[:10],"title":title,"source_type":kind,"body_text":text,
        "source_url":url,"retrieved_at":now(),"verified_at":now(),"content_sha256":sha(text.encode()),
        "response_sha256":sha(raw),"verification_status":"verified","completeness":"provision",
        "valid_from":None,"valid_to":None,"language":"en","jurisdiction":None,
        "interpretation_verified":False,"limits":[]}
UK_ID=re.compile(r"(ukpga|uksi|asp|ssi|anaw|asc|wsi|nia|nisr)/([0-9]{4})/([1-9][0-9]{0,5})")
def uk(ident,provision,asof):
    if not UK_ID.fullmatch(ident) or not re.fullmatch(r"(section|regulation|article)/[1-9][0-9]{0,4}[A-Z]?",provision):raise SourceError("invalid_identifier")
    asof=date(asof);raw,url=fetch("https://www.legislation.gov.uk/"+ident+"/"+provision+"/"+asof+"/data.xml");r=xml(raw)
    expected="/id/"+ident+"/"+provision
    matches=[n for n in r.iter() if urlparse(n.get("IdURI","")).path==expected]
    if len(matches)!=1:raise SourceError("provision_identity_mismatch")
    node=matches[0]
    if not node.get("DocumentURI","").endswith("/"+provision+"/"+asof):raise SourceError("version_identity_mismatch")
    parents={c:p for p in r.iter() for c in p}
    path=[];cur=node
    while cur is not None:path.append(cur);cur=parents.get(cur)
    for n in path:
        a=n.get("RestrictStartDate");b=n.get("RestrictEndDate")
        if (a and asof<a) or (b and asof>=b):raise SourceError("version_interval_mismatch")
    content=[]
    for n in node.iter():
        if local(n)=="Text":content.append(norm(" ".join(n.itertext())))
    if not content:raise SourceError("provision_text_missing")
    text="\n".join(content)
    doc=document("legislation_uk",ident,provision,asof,text,raw,url.removesuffix("/data.xml"),val(r,"title"))
    doc["authority"]="The National Archives / legislation.gov.uk"
    doc["jurisdiction"]="UK; check territorial extent and application"
    doc["territorial_extent"]=next((n.get("RestrictExtent") for n in path if n.get("RestrictExtent")),None)
    doc["valid_from"]=max([n.get("RestrictStartDate") for n in path if n.get("RestrictStartDate")],default=None)
    doc["valid_to_exclusive"]=min([n.get("RestrictEndDate") for n in path if n.get("RestrictEndDate")],default=None)
    doc["unapplied_effects"]=[dict(n.attrib) for n in nodes(r,"UnappliedEffect")]
    doc["applicability_status"]="requires_legal_check"
    doc["licence"]="OGL v3.0; Crown and database right; legislation.gov.uk"
    if val(r,"publisher")=="Westlaw":doc["licence"]+="; Westlaw UK derived from Crown Copyright material and contributed to legislation.gov.uk"
    doc["limits"]=["Exact point-in-time provision retrieved; no certification of commencement, territorial application or transitional rules.","Unapplied effects are document metadata; not all necessarily affect this provision or date."]
    return doc
def sru(query,limit=5):
    if not 1<=limit<=10:raise SourceError("limit_max_10")
    url="https://zoekservice.overheid.nl/sru/Search?"+urlencode({"version":"1.2","operation":"searchRetrieve","x-connection":"BWB","query":query,"maximumRecords":limit})
    raw,_=fetch(url);r=xml(raw)
    if nodes(r,"diagnostic"):raise SourceError("sru_diagnostic")
    return r,raw
def nl(ident,article,asof):
    if not re.fullmatch(r"BWBR[0-9]{7}",ident) or not re.fullmatch(r"[0-9]{1,4}[a-z]?(?:[.:][0-9]{1,4}[a-z]?)?",article):raise SourceError("invalid_identifier")
    asof=date(asof);r,_=sru('dcterms.identifier == '+ident+' and overheidbwb.geldigheidsdatum = '+asof,2)
    records=nodes(r,"record")
    if val(r,"numberOfRecords")!="1" or len(records)!=1:raise SourceError("dated_version_not_unique_or_missing")
    rec=records[0]
    if val(rec,"identifier")!=ident:raise SourceError("identifier_mismatch")
    start=val(rec,"geldigheidsperiode_startdatum");end=val(rec,"geldigheidsperiode_einddatum")
    if not start or not end or not start<=asof<=end:raise SourceError("version_interval_mismatch")
    retrieval=val(rec,"locatie_toestand")
    if not retrieval or urlparse(retrieval).hostname!="repository.officiele-overheidspublicaties.nl":raise SourceError("repository_not_identified")
    raw,url=fetch(retrieval);root=xml(raw)
    if root.get("bwb-id")!=ident:raise SourceError("repository_identity_mismatch")
    selected=[]
    for n in nodes(root,"artikel"):
        kop=n.find("kop")
        if kop is not None and val(kop,"nr")==article:selected.append(n)
    if len(selected)!=1:raise SourceError("article_not_unique_or_missing")
    n=selected[0];start_article=n.get("inwerking")
    if start_article and asof<start_article:raise SourceError("article_not_in_force_at_date")
    parts=[" ".join(c.itertext()) for c in n if local(c)!="meta-data"]
    text=norm(" ".join(parts))
    if len(text)<30:raise SourceError("incomplete_text")
    uri=val(rec,"toestand")
    if not uri or not urlparse(uri).path.startswith("/id/"+ident+"/"):raise SourceError("persistent_identifier_mismatch")
    canonical="https://wetten.overheid.nl/"+ident+"/"+asof+"#"+n.get("bwb-ng-variabel-deel","").strip("/").replace("/","_")
    doc=document("wetten_nl",ident,"art."+article,asof,text,raw,canonical,val(rec,"title"))
    doc.update(authority="KOOP / Basiswettenbestand",jurisdiction="NL",language="nl",valid_from=start,valid_to=end,licence="CC0 1.0; KOOP Basis Wetten Bestand",persistent_version_uri=uri.replace("http:","https:",1),retrieval_url=url,article_effective_from=start_article,source_updated_on=val(rec,"modified"))
    doc["limits"]=["Validity interval refers to the selected consolidated act version; article commencement checked separately.","Original Dutch text; translations and legal interpretation are not certified."]
    return doc
def nl_search(title,asof,limit=5):
    if not 2<=len(title)<=150 or any(x in title for x in ['"',"\\","\n"]):raise SourceError("invalid_search")
    asof=date(asof)
    r,_=sru('overheidbwb.titel = "'+title+'" and overheidbwb.geldigheidsdatum = '+asof,limit)
    return {"status":"partial","source":"wetten_nl","as_of":asof,"total":val(r,"numberOfRecords"),
        "results":[{"official_id":val(n,"identifier"),"title":val(n,"title"),"valid_from":val(n,"geldigheidsperiode_startdatum"),"valid_to":val(n,"geldigheidsperiode_einddatum")} for n in nodes(r,"record")],
        "limits":["Bounded metadata discovery; retrieve the provision before citation."]}
def guidance(url):
    p=urlparse(url)
    if p.hostname!="www.belastingdienst.nl" or not p.path.startswith("/wps/wcm/connect/") or p.query or p.fragment:raise SourceError("guidance_url_not_allowed")
    raw,final=fetch(url);s=BeautifulSoup(raw,"html.parser");main=s.find("main");h=s.find("h1")
    if main is None or h is None:raise SourceError("guidance_content_not_identified")
    for t in main.find_all(["script","style","nav","footer"]):t.decompose()
    article=main.find("article") or main;text=norm(article.get_text(" ",strip=True))
    if len(text)<200 or any(x in text.lower() for x in ["access denied","verify you are human"]):raise SourceError("guidance_incomplete_or_blocked")
    doc=document("belastingdienst",final,"official-guidance",None,text,raw,final,h.get_text(" ",strip=True),"guidance")
    doc.update(authority="Belastingdienst",jurisdiction="NL",language=s.html.get("lang","unknown"),completeness="page_text",licence="CC0 unless a component states an exception; Belastingdienst copyright notice")
    doc["applicability_status"]="not_legislation"
    doc["limits"]=["Administrative guidance, not statutory text or an individual tax decision.","No historical version or effective date is inferred; check the legal basis and tax year independently."]
    return doc
def verify(c):
    try:
        source=c.get("source")
        if source=="legislation_uk":d=uk(c["official_id"],c["provision"],c["as_of"])
        elif source=="wetten_nl":d=nl(c["official_id"],str(c["article"]),c["as_of"])
        elif source=="belastingdienst":d=guidance(c["url"])
        elif source=="find_case_law":raise SourceError("computational_connector_not_enabled_licensing_pending")
        else:raise SourceError("source_not_integrated")
        q=c.get("quote")
        if not isinstance(q,str) or len(norm(q))<12:status="partial";reason="precise_passage_missing"
        elif norm(q) not in norm(d["body_text"]):status="unverified";reason="quoted_passage_not_supported"
        else:status="verified";reason="official_identity_version_and_literal_passage_checked"
        return {"status":status,"reason":reason,"checked_at":now(),"official_id":d["official_id"],"source_url":d["source_url"],"version":d["version_label"],"source_type":d["source_type"],"interpretation_verified":False,"applicability_status":d.get("applicability_status","selected_version_checked"),"limits":d["limits"]}
    except (SourceError,KeyError,ValueError,TypeError) as e:return {"status":"unverified","reason":str(e) if isinstance(e,SourceError) else "invalid_citation","checked_at":now(),"interpretation_verified":False,"limits":["Failure to verify does not establish non-existence."]}
def save(d):
    DATA.mkdir(parents=True,exist_ok=True,mode=0o700)
    f=DATA/(sha((d["source_key"]+d["official_id"]+d["locator"]+d["version_label"]).encode())+".json")
    temp=f.with_suffix(".tmp");temp.write_text(json.dumps(d,ensure_ascii=False,indent=2));temp.chmod(0o600);temp.replace(f)
    return str(f)

def db_init():
    from lex_engine import connection
    with connection() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS lex_intl_records(
          id bigserial PRIMARY KEY, source_key text NOT NULL, official_id text NOT NULL,
          locator text NOT NULL, version_label text NOT NULL, applicable_on date,
          valid_from date, valid_to date, retrieved_at timestamptz NOT NULL,
          language text NOT NULL, body_text text NOT NULL, content_sha256 text NOT NULL,
          evidence jsonb NOT NULL,
          search_vector tsvector GENERATED ALWAYS AS (
            to_tsvector(CASE WHEN language='nl' THEN 'dutch'::regconfig ELSE 'english'::regconfig END,body_text)
          ) STORED,
          UNIQUE(source_key,official_id,locator,version_label,content_sha256))""")
        c.execute("CREATE INDEX IF NOT EXISTS lex_intl_records_fts ON lex_intl_records USING gin(search_vector)")
    return {"database":"lex_legal","table":"lex_intl_records","status":"prepared"}
def archive(d):
    from lex_engine import connection
    from psycopg.types.json import Jsonb
    with connection() as c:
        keys=["source_key","official_id","locator","version_label","applicable_on","valid_from","valid_to","retrieved_at","language","body_text","content_sha256"]
        c.execute("INSERT INTO lex_intl_records("+",".join(keys)+",evidence) VALUES("+",".join(["%s"]*(len(keys)+1))+") ON CONFLICT DO NOTHING",
          tuple(d.get(k) for k in keys)+(Jsonb(d),))
    return {"archived":True,"database":"lex_legal","table":"lex_intl_records"}
def dbsearch(q,source,asof=None):
    from lex_engine import connection
    if not 2<=len(q)<=250 or source not in ["legislation_uk","wetten_nl","belastingdienst"]:raise SourceError("invalid_search")
    if asof:asof=date(asof)
    language="dutch" if source=="wetten_nl" else "english"
    with connection() as c:
        rows=c.execute("""SELECT official_id,locator,version_label,evidence->>'source_url',retrieved_at,
          ts_headline(%s::regconfig,body_text,websearch_to_tsquery(%s::regconfig,%s),'MaxWords=50,MinWords=15')
          FROM lex_intl_records
          WHERE source_key=%s AND search_vector @@ websearch_to_tsquery(%s::regconfig,%s)
          AND (%s::date IS NULL OR applicable_on=%s::date)
          ORDER BY retrieved_at DESC LIMIT 10""",(language,language,q,source,language,q,asof,asof)).fetchall()
    return {"source":source,"results":[dict(zip(["official_id","locator","version","url","retrieved_at","excerpt"],r)) for r in rows],
      "limits":["Selected corpus only; dated search requires a snapshot requested at that date. Retrieve afresh before citation."]}

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("uk");a.add_argument("--id",required=True);a.add_argument("--provision",required=True);a.add_argument("--as-of",required=True)
    a=s.add_parser("nl");a.add_argument("--id",required=True);a.add_argument("--article",required=True);a.add_argument("--as-of",required=True)
    a=s.add_parser("nl-search");a.add_argument("title");a.add_argument("--as-of",required=True);a.add_argument("--limit",type=int,default=5)
    a=s.add_parser("guidance");a.add_argument("--url",required=True)
    a=s.add_parser("verify");a.add_argument("--citation-file",required=True)
    a=s.add_parser("db-search");a.add_argument("query");a.add_argument("--source",required=True);a.add_argument("--as-of")
    for command in ("uk","nl","guidance"):s.choices[command].add_argument("--archive",action="store_true")
    args=p.parse_args()
    try:
        if args.cmd=="uk":out=uk(args.id,args.provision,args.as_of)
        elif args.cmd=="nl":out=nl(args.id,args.article,args.as_of)
        elif args.cmd=="nl-search":out=nl_search(args.title,args.as_of,args.limit)
        elif args.cmd=="guidance":out=guidance(args.url)
        elif args.cmd=="db-search":out=dbsearch(args.query,args.source,args.as_of)
        else:out=verify(json.loads(pathlib.Path(args.citation_file).read_text()))
        if args.cmd in ("uk","nl","guidance"):
            out["snapshot_path"]=save(out)
            if args.archive:out["archive"]=archive(out)
        if "unapplied_effects" in out:
            effects=out["unapplied_effects"]
            out["unapplied_effects_count"]=len(effects)
            out["unapplied_effects"]=effects[:3]
            out["unapplied_effects_truncated"]=len(effects)>3
            out["limits"].append("Full unapplied-effects metadata is retained in snapshot_path; terminal output shows at most three effects.")
        print(json.dumps(out,ensure_ascii=False,indent=2));return 2 if out.get("status")=="unverified" else 0
    except Exception as e:
        reason=str(e) if isinstance(e,SourceError) else "internal_error_"+type(e).__name__
        print(json.dumps({"status":"unverified","reason":reason,"checked_at":now()}));return 2
if __name__=="__main__":sys.exit(main())
