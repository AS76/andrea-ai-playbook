#!/usr/bin/env python3
import concurrent.futures, json, pathlib, resource, time, sys
import lex_international as m
import lex_engine as old
results=[];docs={}
def run(name,fn):
    t=time.monotonic()
    try:
        d=fn();results.append({"test":name,"status":"PASS","seconds":round(time.monotonic()-t,3),"detail":d})
    except Exception as e:results.append({"test":name,"status":"FAIL","reason":type(e).__name__+":"+str(e)[:180]})
def retrieve(label,fn):
    d=fn();docs[label]=d;m.save(d);m.archive(d)
    return {k:d[k] for k in ["official_id","locator","source_url","content_sha256","source_type"]}
def expect_error(fn,reason):
    try:fn()
    except m.SourceError as e:
        assert str(e)==reason,str(e);return reason
    raise AssertionError("expected rejection")
def check(c,status):
    v=m.verify(c);assert v["status"]==status,v;assert not v["interpretation_verified"];return v
run("uk_historical",lambda:retrieve("uk_old",lambda:m.uk("ukpga/1996/18","section/1","2020-01-01")))
run("uk_current",lambda:retrieve("uk_now",lambda:m.uk("ukpga/1996/18","section/1","2026-10-11")))
run("uk_versions_differ",lambda: {"different": True} if docs["uk_old"]["content_sha256"]!=docs["uk_now"]["content_sha256"] else (_ for _ in ()).throw(AssertionError("same versions")))
run("nl_historical",lambda:retrieve("nl_old",lambda:m.nl("BWBR0005290","611","2020-01-01")))
run("nl_current",lambda:retrieve("nl_now",lambda:m.nl("BWBR0005290","611","2026-10-11")))
run("nl_contract_changes",lambda:retrieve("nl_613",lambda:m.nl("BWBR0005290","613","2026-10-11")))
run("nl_fiscal_statute",lambda:retrieve("nl_tax",lambda:m.nl("BWBR0011353","2.1","2026-10-11")))
run("belasting_guidance",lambda:retrieve("guide",lambda:m.guidance("https://www.belastingdienst.nl/wps/wcm/connect/en/individuals/content/coming-to-work-in-the-netherlands-30-percent-facility")))
run("uk_literal_verification",lambda:check({"source":"legislation_uk","official_id":"ukpga/1996/18","provision":"section/1","as_of":"2020-01-01","quote":"Where an employee begins employment with an employer"},"verified"))
run("nl_literal_verification",lambda:check({"source":"wetten_nl","official_id":"BWBR0005290","article":"611","as_of":"2026-10-11","quote":"De werkgever en de werknemer zijn verplicht zich als een goed werkgever"},"verified"))
run("invented_quote_rejected",lambda:check({"source":"wetten_nl","official_id":"BWBR0005290","article":"611","as_of":"2026-10-11","quote":"TGW must transfer Andrea to the Netherlands immediately"},"unverified"))
run("invented_article_rejected",lambda:check({"source":"wetten_nl","official_id":"BWBR0005290","article":"9999","as_of":"2026-10-11","quote":"Invented article not present in statute"},"unverified"))
run("historical_wrong_quote_rejected",lambda:check({"source":"legislation_uk","official_id":"ukpga/1996/18","provision":"section/1","as_of":"2020-01-01","quote":"Where a worker begins employment with an employer"},"unverified"))
run("unlicensed_connector_disabled",lambda:check({"source":"find_case_law"},"unverified"))
run("private_host_rejected",lambda:expect_error(lambda:m.fetch("https://127.0.0.1/"),"source_not_allowed"))
run("future_date_rejected",lambda:expect_error(lambda:m.nl("BWBR0005290","611","2099-01-01"),"future_date_not_supported"))
run("xxe_rejected",lambda:expect_error(lambda:m.xml(b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><a>&x;</a>'),"invalid_or_unsafe_xml"))
def fts():
    d=m.dbsearch("werkgever","wetten_nl","2026-10-11");assert d["results"];return {"hits":len(d["results"])}
run("dutch_fulltext",fts)
def fts_en():
    d=m.dbsearch("employee","legislation_uk","2020-01-01");assert d["results"];return {"hits":len(d["results"])}
run("english_fulltext",fts_en)
def dedupe():
    from lex_engine import connection
    with connection() as c:a=c.execute("SELECT count(*) FROM lex_intl_records").fetchone()[0]
    m.archive(docs["nl_now"])
    with connection() as c:b=c.execute("SELECT count(*) FROM lex_intl_records").fetchone()[0]
    assert a==b;return {"before":a,"after":b}
run("deduplication",dedupe)
def regression():
    d=old.normattiva("urn:nir:stato:legge:1990-08-07;241","1","2026-10-11")
    assert "collaborazione e della buona fede" in d["body_text"]
    return {"source":d["source_key"],"hash":d["content_sha256"]}
run("italian_connector_regression",regression)
def load():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        ds=list(pool.map(lambda _:m.nl("BWBR0005290","611","2026-10-11"),range(2)))
    assert all(x["content_sha256"]==docs["nl_now"]["content_sha256"] for x in ds)
    return {"workers":2,"documents":2}
run("moderate_concurrency",load)
report={"executed_at":m.now(),"results":results,"peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"cpu_seconds":round(resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,3)}
path=pathlib.Path(__file__).with_name("test-international-results.json");path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(1 if any(x["status"]=="FAIL" for x in results) else 0)
