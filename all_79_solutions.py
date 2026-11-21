from __future__ import annotations
import asyncio
from collections import Counter, OrderedDict, defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from functools import wraps
from heapq import heappush, heappop
from math import log, sqrt
from pathlib import Path
import csv
import json
import random
import re
import threading
import time
from typing import Any, Callable, Iterable, Iterator

# 1-10 Arrays and hashing

def q01_two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen: return [seen[target-x], i]
        seen[x] = i
    return []

def q02_contains_duplicate(nums: list[int]) -> bool:
    return len(nums) != len(set(nums))

def q03_valid_anagram(a: str, b: str) -> bool:
    return Counter(a) == Counter(b)

def q04_first_non_repeating(s: str) -> str | None:
    counts = Counter(s)
    return next((c for c in s if counts[c] == 1), None)

def q05_char_frequency(s: str) -> dict[str, int]:
    return dict(Counter(s))

def q06_group_anagrams(words: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for w in words: groups[tuple(sorted(w))].append(w)
    return list(groups.values())

def q07_top_k_frequent(nums: list[int], k: int) -> list[int]:
    return [n for n, _ in Counter(nums).most_common(k)]

def q08_product_except_self(nums: list[int]) -> list[int]:
    result = [1]*len(nums)
    prefix = 1
    for i, n in enumerate(nums): result[i], prefix = prefix, prefix*n
    suffix = 1
    for i in range(len(nums)-1, -1, -1): result[i], suffix = result[i]*suffix, suffix*nums[i]
    return result

def q09_majority_element(nums: list[int]) -> int | None:
    if not nums: return None
    candidate, count = None, 0
    for n in nums:
        if count == 0: candidate = n
        count += 1 if n == candidate else -1
    return candidate if nums.count(candidate) > len(nums)//2 else None

def q10_intersection(a: list[int], b: list[int]) -> list[int]:
    return sorted(set(a) & set(b))

# 11-16 Strings/sliding windows

def q11_longest_unique_substring(s: str) -> int:
    seen, left, best = {}, 0, 0
    for right, c in enumerate(s):
        if c in seen and seen[c] >= left: left = seen[c]+1
        seen[c] = right
        best = max(best, right-left+1)
    return best

def q12_valid_palindrome(s: str) -> bool:
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]

def q13_longest_common_prefix(words: list[str]) -> str:
    if not words: return ''
    prefix = words[0]
    for w in words[1:]:
        while not w.startswith(prefix): prefix = prefix[:-1]
    return prefix

def q14_find_all_anagrams(s: str, p: str) -> list[int]:
    if not p or len(p) > len(s): return []
    target, window = Counter(p), Counter(s[:len(p)])
    found = [0] if window == target else []
    for i in range(len(p),len(s)):
        window[s[i]] += 1
        old = s[i-len(p)]; window[old] -= 1
        if window[old] == 0: del window[old]
        if window == target: found.append(i-len(p)+1)
    return found

def q15_longest_palindromic_substring(s: str) -> str:
    best = ''
    for center in range(len(s)):
        for l,r in ((center,center),(center,center+1)):
            while l>=0 and r<len(s) and s[l]==s[r]: l-=1; r+=1
            if r-l-1>len(best): best=s[l+1:r]
    return best

def q16_min_window_substring(s: str,t: str) -> str:
    if not t: return ''
    need=Counter(t); missing=len(t); left=0; best=(float('inf'),0,0)
    for right,c in enumerate(s):
        if need[c]>0: missing-=1
        need[c]-=1
        while missing==0:
            if right-left+1 < best[0]: best=(right-left+1,left,right+1)
            old=s[left];need[old]+=1;left+=1
            if need[old]>0: missing+=1
    return s[best[1]:best[2]] if best[0] != float('inf') else ''

# 17-21 Two pointers / greedy

def q17_max_stock_profit(prices: list[int]) -> int:
    low=float('inf'); profit=0
    for p in prices: low=min(low,p);profit=max(profit,p-low)
    return profit

def q18_move_zeroes(nums: list[int]) -> list[int]:
    write=0
    for x in nums:
        if x!=0: nums[write]=x; write+=1
    nums[write:]=[0]*(len(nums)-write)
    return nums

def q19_remove_duplicates_sorted(nums: list[int]) -> int:
    if not nums: return 0
    write=1
    for read in range(1,len(nums)):
        if nums[read] != nums[write-1]: nums[write]=nums[read];write+=1
    return write  # valid unique prefix is nums[:write]

def q20_max_subarray(nums: list[int]) -> int:
    if not nums: raise ValueError('nonempty array required')
    best=current=nums[0]
    for x in nums[1:]: current=max(x,current+x);best=max(best,current)
    return best

def q21_three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort();out=[]
    for i,a in enumerate(nums):
        if i and a==nums[i-1]: continue
        l,r=i+1,len(nums)-1
        while l<r:
            total=a+nums[l]+nums[r]
            if total<0:l+=1
            elif total>0:r-=1
            else:
                out.append([a,nums[l],nums[r]]);l+=1;r-=1
                while l<r and nums[l]==nums[l-1]:l+=1
                while l<r and nums[r]==nums[r+1]:r-=1
    return out

# 22-26 Stack, linked list, cache

def q22_valid_parentheses(s: str) -> bool:
    pairs={')':'(',']':'[','}':'{'};stack=[]
    for c in s:
        if c in '([{':stack.append(c)
        elif c in pairs:
            if not stack or stack.pop()!=pairs[c]:return False
        else:return False
    return not stack

class Q23LRUCache:
    """OrderedDict gives amortized O(1) get and put in Python."""
    def __init__(self,capacity:int):
        if capacity<=0:raise ValueError('capacity must be positive')
        self.capacity=capacity;self.data=OrderedDict()
    def get(self,key:int)->int:
        if key not in self.data:return -1
        self.data.move_to_end(key);return self.data[key]
    def put(self,key:int,value:int)->None:
        self.data[key]=value;self.data.move_to_end(key)
        if len(self.data)>self.capacity:self.data.popitem(last=False)

class Q24MinStack:
    def __init__(self):self.values=[];self.minimums=[]
    def push(self,x:int)->None:
        self.values.append(x)
        self.minimums.append(min(x,self.minimums[-1] if self.minimums else x))
    def pop(self)->int:self.minimums.pop();return self.values.pop()
    def top(self)->int:return self.values[-1]
    def get_min(self)->int:return self.minimums[-1]

@dataclass
class ListNode:
    val:int
    next:ListNode|None=None

def q25_reverse_linked_list(head:ListNode|None)->ListNode|None:
    prev=None
    while head:head.next,prev,head=prev,head,head.next
    return prev

def q26_linked_list_cycle(head:ListNode|None)->bool:
    slow=fast=head
    while fast and fast.next:
        slow=slow.next;fast=fast.next.next
        if slow is fast:return True
    return False

# 27-30 Search, intervals, BFS

def q27_binary_search(nums:list[int],target:int)->int:
    lo,hi=0,len(nums)-1
    while lo<=hi:
        m=(lo+hi)//2
        if nums[m]==target:return m
        if nums[m]<target:lo=m+1
        else:hi=m-1
    return -1

def q28_search_rotated(nums:list[int],target:int)->int:
    """Assumes distinct values."""
    lo,hi=0,len(nums)-1
    while lo<=hi:
        m=(lo+hi)//2
        if nums[m]==target:return m
        if nums[lo]<=nums[m]:
            if nums[lo]<=target<nums[m]:hi=m-1
            else:lo=m+1
        else:
            if nums[m]<target<=nums[hi]:lo=m+1
            else:hi=m-1
    return -1

def q29_merge_intervals(intervals:list[list[int]])->list[list[int]]:
    out=[]
    for start,end in sorted(intervals):
        if not out or start>out[-1][1]:out.append([start,end])
        else:out[-1][1]=max(out[-1][1],end)
    return out

def q30_bfs_shortest_path(graph:dict[Any,list[Any]],src:Any,dst:Any)->list[Any]:
    queue=deque([src]);parents={src:None}
    while queue:
        node=queue.popleft()
        if node==dst:
            path=[]
            while node is not None:path.append(node);node=parents[node]
            return path[::-1]
        for nxt in graph.get(node,[]):
            if nxt not in parents:parents[nxt]=node;queue.append(nxt)
    return []

# 31-45 Core Python
class Q31BankAccount:
    def __init__(self,account_id:str,balance:float=0):
        if balance<0:raise ValueError('negative opening balance')
        self.account_id=account_id;self._balance=balance;self._lock=threading.Lock()
    @property
    def balance(self)->float:return self._balance
    def deposit(self,amount:float)->float:
        if amount<=0:raise ValueError('positive amount required')
        with self._lock:self._balance+=amount;return self._balance
    def withdraw(self,amount:float)->float:
        if amount<=0:raise ValueError('positive amount required')
        with self._lock:
            if amount>self._balance:raise ValueError('insufficient funds')
            self._balance-=amount;return self._balance
    # Real money: use Decimal and database transactions, not floats or process-local locks.

@dataclass(frozen=True)
class Q32Invoice:
    invoice_id:str
    vendor:str
    amount_cents:int
    due_date:date

def q33_timed(func:Callable)->Callable:
    @wraps(func)
    def wrapper(*args,**kwargs):
        start=time.perf_counter()
        try:return func(*args,**kwargs)
        finally:print(f'{func.__name__}: {time.perf_counter()-start:.4f}s')
    return wrapper

def q34_retry(attempts:int=3,base_delay:float=.1):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args,**kwargs):
            for i in range(attempts):
                try:return fn(*args,**kwargs)
                except (TimeoutError,ConnectionError):
                    if i==attempts-1:raise
                    time.sleep(base_delay*(2**i))
        return wrapper
    return decorate

def q35_paginate(fetch_page:Callable[[int],list],start_page:int=1)->Iterator[Any]:
    page=start_page
    while True:
        rows=fetch_page(page)
        if not rows:break
        yield from rows
        page+=1

@contextmanager
def q36_timing_context(label:str):
    start=time.perf_counter()
    try:yield
    finally:print(f'{label}: {time.perf_counter()-start:.4f}s')

class Q37Employee:
    def __init__(self,name:str):self.name=name
    def description(self)->str:return f'Employee {self.name}'
class Q37Engineer(Q37Employee):
    def description(self)->str:return f'Engineer {self.name}'

class Q38Singleton:
    _instance=None
    def __new__(cls):
        if cls._instance is None:cls._instance=super().__new__(cls)
        return cls._instance
    # For production, dependency-injected shared instances are generally clearer.

def q39_describe_call(*args,**kwargs)->dict:
    return {'positional':list(args),'keyword':kwargs}

def q40_nested_get(obj:dict,path:list[str],default=None):
    value=obj
    for key in path:
        if not isinstance(value,dict) or key not in value:return default
        value=value[key]
    return value

def q41_flatten(values:list)->list:
    result=[]
    for x in values:
        if isinstance(x,list):result.extend(q41_flatten(x))
        else:result.append(x)
    return result

class Q42TTLCache:
    def __init__(self,ttl_seconds:float):self.ttl=ttl_seconds;self.entries={}
    def put(self,key,value):self.entries[key]=(value,time.monotonic()+self.ttl)
    def get(self,key,default=None):
        entry=self.entries.get(key)
        if entry is None:return default
        value,expires=entry
        if time.monotonic()>=expires:self.entries.pop(key,None);return default
        return value

def q43_stream_csv(path:str|Path)->Iterator[dict[str,str]]:
    with open(path,newline='',encoding='utf-8') as f:
        yield from csv.DictReader(f)

def q44_dedup_transactions(rows:list[dict])->list[dict]:
    seen=set();out=[]
    for row in rows:
        txn=row['transaction_id']
        if txn not in seen:seen.add(txn);out.append(row)
    return out

def q45_sort_invoices(rows:list[dict])->list[dict]:
    return sorted(rows,key=lambda x:(x['due_date'],x['amount']))

# 46-57 FastAPI + asyncio
# For 46-51, 56 and 57, see the companion fastapi_app.py / test_fastapi_app.py.
# 52, concurrent calls
async def q52_fetch_parallel(invoice_fn,vendor_fn,payment_fn)->dict:
    invoice,vendor,payment=await asyncio.gather(invoice_fn(),vendor_fn(),payment_fn())
    return {'invoice':invoice,'vendor':vendor,'payment':payment}

# 53, timeout
async def q53_with_timeout(coro,seconds:float):
    return await asyncio.wait_for(coro,timeout=seconds)

# 54, bounded retry with jitter, intended only for idempotent requests
async def q54_retry_async(fn:Callable,attempts:int=3,base_delay:float=.1):
    for i in range(attempts):
        try:return await fn()
        except (TimeoutError,ConnectionError):
            if i==attempts-1:raise
            await asyncio.sleep(base_delay*2**i+random.uniform(0,base_delay))

# 55, concurrency control (share same semaphore among calls)
Q55_SEMAPHORE=asyncio.Semaphore(5)
async def q55_limited_llm_call(llm_fn:Callable):
    async with Q55_SEMAPHORE:return await llm_fn()

# 58-69 RAG/agent engineering

def q58_fixed_chunks(text:str,size:int=100,overlap:int=20)->list[str]:
    if size<=0 or not 0<=overlap<size:raise ValueError('0 <= overlap < size required')
    return [text[i:i+size] for i in range(0,len(text),size-overlap)] if text else []

def q59_recursive_split(text:str,max_chars:int=100,separators:tuple[str,...]=('\n\n','\n','. ',' '))->list[str]:
    if max_chars<=0:raise ValueError('max_chars positive')
    if len(text)<=max_chars:return [text] if text else []
    for sep in separators:
        if sep not in text:continue
        units=text.split(sep);chunks=[];current=''
        for unit in units:
            piece=unit if not current else sep+unit
            if len(current+piece)>max_chars and current:
                chunks.extend(q59_recursive_split(current,max_chars,tuple(s for s in separators if s!=sep)))
                current=unit
            else:current+=piece
        if current:chunks.extend(q59_recursive_split(current,max_chars,tuple(s for s in separators if s!=sep)))
        return chunks
    return q58_fixed_chunks(text,max_chars,0)

def q60_cosine_similarity(a:list[float],b:list[float])->float:
    if len(a)!=len(b):raise ValueError('vector dimensions differ')
    norm_a=sqrt(sum(x*x for x in a));norm_b=sqrt(sum(x*x for x in b))
    return sum(x*y for x,y in zip(a,b))/(norm_a*norm_b) if norm_a and norm_b else 0.0

def q61_topk_vectors(query:list[float],vectors:dict[str,list[float]],k:int)->list[tuple[str,float]]:
    return sorted(((doc,q60_cosine_similarity(query,vec)) for doc,vec in vectors.items()),key=lambda x:x[1],reverse=True)[:k]

def q62_bm25_search(query:str,docs:dict[str,str],k:int=3,k1:float=1.5,b:float=.75)->list[tuple[str,float]]:
    """Small, self-contained BM25; tokenization is intentionally basic."""
    terms={name:re.findall(r'\w+',text.lower()) for name,text in docs.items()}
    qterms=re.findall(r'\w+',query.lower());n=len(terms)
    if not n:return []
    avgdl=sum(map(len,terms.values()))/n or 1
    df=Counter(t for tokens in terms.values() for t in set(tokens));out=[]
    for name,tokens in terms.items():
        tf=Counter(tokens);score=0.0
        for term in qterms:
            f=tf[term]
            if f:
                idf=log(1+(n-df[term]+.5)/(df[term]+.5))
                score+=idf*f*(k1+1)/(f+k1*(1-b+b*len(tokens)/avgdl))
        out.append((name,score))
    return sorted(out,key=lambda x:x[1],reverse=True)[:k]

def q63_rrf(rankings:list[list[str]],k:int=60)->list[tuple[str,float]]:
    scores=defaultdict(float)
    for ranking in rankings:
        for rank,doc in enumerate(ranking,1):scores[doc]+=1/(k+rank)
    return sorted(scores.items(),key=lambda p:p[1],reverse=True)

def q64_rerank(query:str,docs:dict[str,str])->list[tuple[str,int]]:
    """Demo lexical overlap reranker, NOT a trained cross-encoder."""
    q=set(query.lower().split())
    return sorted(((name,len(q&set(text.lower().split()))) for name,text in docs.items()),key=lambda p:p[1],reverse=True)

def q65_simple_rag(query:str,docs:dict[str,str],llm_fn:Callable[[str],str],k:int=3)->str:
    matches=q62_bm25_search(query,docs,k)
    context='\n'.join(f'[{doc}] {docs[doc]}' for doc,_ in matches)
    return llm_fn(f'Answer only from context; if insufficient, say you do not know.\nContext:\n{context}\nQuestion: {query}')

def q66_rewrite_followup(history:list[str],question:str,llm_fn:Callable[[str],str])->str:
    prompt=f'Rewrite follow-up as standalone question; preserve entities.\nHistory: {history[-4:]}\nFollow-up: {question}'
    return llm_fn(prompt)

def q67_precision_at_k(relevant:set[str],retrieved:list[str],k:int)->float:
    if k<=0:raise ValueError('k must be positive')
    return len(set(retrieved[:k])&relevant)/k

def q67_recall_at_k(relevant:set[str],retrieved:list[str],k:int)->float:
    if k<=0:raise ValueError('k must be positive')
    return len(set(retrieved[:k])&relevant)/len(relevant) if relevant else 0.0

def q67_mrr(queries:list[tuple[set[str],list[str]]])->float:
    if not queries:return 0.0
    return sum(next((1/i for i,d in enumerate(ranked,1) if d in relevant),0.0) for relevant,ranked in queries)/len(queries)

# Q68 Pydantic output schema: see fastapi_app.py. This convenience validator is optional-package guarded.
def q68_validate_llm_json(text:str)->dict:
    from pydantic import BaseModel, Field
    class Answer(BaseModel):
        answer:str=Field(min_length=1)
        confidence:float=Field(ge=0,le=1)
    return Answer.model_validate_json(text).model_dump()

def q69_agent_loop(model_fn:Callable[[list[dict]],dict],tools:dict[str,Callable],messages:list[dict],max_steps:int=5)->dict:
    """Minimal synchronous tool agent; real implementations need tool permissions and timeouts."""
    history=list(messages);seen=Counter()
    for _ in range(max_steps):
        response=model_fn(history)
        if 'final' in response:return {'status':'finished','answer':response['final'],'history':history}
        tool_name,args=response.get('tool'),response.get('args',{})
        if tool_name not in tools or not isinstance(args,dict):
            return {'status':'invalid_tool','history':history}
        signature=json.dumps([tool_name,args],sort_keys=True)
        seen[signature]+=1
        if seen[signature]>2:return {'status':'repeated_tool_loop','history':history}
        try:result=tools[tool_name](**args)
        except Exception as exc:result={'error':type(exc).__name__}
        history.append({'role':'tool','name':tool_name,'result':result})
    return {'status':'max_steps','history':history}

# 70-79 Finance

def q70_duplicate_invoices(invoices:list[dict])->list[dict]:
    seen=set();duplicates=[]
    for row in invoices:
        key=(row['vendor'],row['invoice_no'],row['amount'])
        if key in seen:duplicates.append(row)
        else:seen.add(key)
    return duplicates

def q71_match_purchase_orders(invoices:list[dict],purchase_orders:list[dict])->list[dict]:
    orders={po['po_id']:po for po in purchase_orders};matches=[]
    for inv in invoices:
        po=orders.get(inv.get('po_id'))
        matches.append({'invoice':inv,'matched':bool(po and po['vendor']==inv['vendor'] and po['amount']==inv['amount'])})
    return matches

def q72_vendor_totals(transactions:list[dict])->dict[str,float]:
    totals=defaultdict(float)
    for t in transactions:totals[t['vendor']]+=t['amount']
    return dict(totals)

def q73_overdue_invoices(invoices:list[dict],as_of:date,days:int=30)->list[dict]:
    return [i for i in invoices if (as_of-i['due_date']).days>days and i.get('status')!='paid']

def q74_reconcile_payments(invoices:list[dict],payments:list[dict])->list[dict]:
    paid=defaultdict(float)
    for p in payments:paid[p['invoice_id']]+=p['amount']
    return [{'invoice_id':i['invoice_id'],'expected':i['amount'],'paid':paid[i['invoice_id']],
             'difference':round(i['amount']-paid[i['invoice_id']],2)} for i in invoices]

def q75_amount_outliers(amounts:list[float],threshold:float=3)->list[float]:
    """Simple population z-score, not an adequate standalone fraud model."""
    if len(amounts)<2:return []
    avg=sum(amounts)/len(amounts)
    sd=sqrt(sum((x-avg)**2 for x in amounts)/len(amounts))
    return [x for x in amounts if sd>0 and abs(x-avg)/sd>threshold]

def q76_extract_invoice_json(payload:str)->dict:
    obj=json.loads(payload)
    return {key:obj[key] for key in ('vendor','invoice_no','amount','due_date')}

def q77_validate_invoice_row(row:dict)->dict:
    required=('vendor','invoice_no','amount')
    missing=[key for key in required if row.get(key) in (None,'')]
    if missing:raise ValueError(f'Missing: {missing}')
    try:amount=float(row['amount'])
    except (ValueError,TypeError) as exc:raise ValueError('Invalid amount') from exc
    if amount<0:raise ValueError('Negative amount')
    return {'vendor':str(row['vendor']).strip(),'invoice_no':str(row['invoice_no']).strip(),'amount':amount}

Q78_TOP_FIVE_VENDORS_SQL = """
SELECT vendor_id, SUM(amount) AS total_spend
FROM invoices
WHERE status = 'paid'
GROUP BY vendor_id
ORDER BY total_spend DESC
LIMIT 5;
"""
Q79_SECOND_HIGHEST_SQL = """
SELECT MAX(amount) AS second_highest_amount
FROM invoices
WHERE amount < (SELECT MAX(amount) FROM invoices);
"""

if __name__=='__main__':
    assert q01_two_sum([2,7,11,15],9)==[0,1]
    assert q04_first_non_repeating('swiss')=='w'
    assert q06_group_anagrams(['eat','tea','bat'])==[['eat','tea'],['bat']]
    assert q08_product_except_self([1,2,3,4])==[24,12,8,6]
    assert q11_longest_unique_substring('abcabcbb')==3
    assert q14_find_all_anagrams('cbaebabacd','abc')==[0,6]
    assert q16_min_window_substring('ADOBECODEBANC','ABC')=='BANC'
    assert q21_three_sum([-1,0,1,2,-1,-4])==[[-1,-1,2],[-1,0,1]]
    assert q22_valid_parentheses('({[]})')
    cache=Q23LRUCache(2);cache.put(1,1);cache.put(2,2);cache.get(1);cache.put(3,3)
    assert cache.get(2)==-1
    assert q28_search_rotated([4,5,6,7,0,1,2],0)==4
    assert q29_merge_intervals([[1,3],[2,6],[8,10]])==[[1,6],[8,10]]
    assert q58_fixed_chunks('abcdef',4,2)==['abcd','cdef','ef']
    assert q67_recall_at_k({'doc1','doc3','doc5'},['doc3','doc8','doc1'],3)==2/3
    print('Selected smoke tests passed. Run pytest for additional tests.')
