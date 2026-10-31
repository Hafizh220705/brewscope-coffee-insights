#!/usr/bin/env python3
"""Validate BrewScope canonical annotation JSONL. Requires jsonschema."""
import argparse, json, collections
import jsonschema
ASPECTS={'product_quality','service','price_value','ambience','facilities','cleanliness'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',default='annotations_full.jsonl');p.add_argument('--schema',default='annotation_schema.json');args=p.parse_args()
 schema=json.load(open(args.schema,encoding='utf-8'))
 checker=jsonschema.Draft202012Validator(schema)
 ids=set();reviews=collections.defaultdict(set);total=0;errors=[]
 with open(args.input,encoding='utf-8') as f:
  for lineno,line in enumerate(f,1):
   if not line.strip():continue
   obj=json.loads(line);total+=1
   for e in checker.iter_errors(obj):errors.append(f'line {lineno}: {e.message}')
   key=obj.get('annotation_id')
   if key in ids:errors.append(f'line {lineno}: duplicate annotation_id')
   ids.add(key)
   rid=obj.get('review_id');a=obj.get('aspect_category')
   if a in reviews[rid]:errors.append(f'line {lineno}: duplicate review/aspect')
   reviews[rid].add(a)
   text=obj.get('review_text','')
   for e in obj.get('evidence',[]):
    start=e.get('start',-1);end=e.get('end',-1)
    if not(isinstance(start,int) and isinstance(end,int) and 0<=start<end<=len(text) and text[start:end]==e.get('quote')):
     errors.append(f'line {lineno}: incorrect evidence offset')
 for rid,aset in reviews.items():
  if aset!=ASPECTS:errors.append(f'review {rid}: {len(aset)} aspects, incorrect set')
 print(json.dumps({'total_records':total,'reviews':len(reviews),'errors':len(errors),'first_errors':errors[:15]},indent=2))
 raise SystemExit(1 if errors else 0)
if __name__=='__main__':main()
