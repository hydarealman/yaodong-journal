(() => {
 const tree=document.querySelector('.outline-tree'),panel=document.querySelector('#article-outline');
 if(!tree||!panel)return;
 const buttons=[];
 tree.querySelectorAll('li').forEach(li=>{
  const link=li.querySelector(':scope > a'),child=li.querySelector(':scope > ul');
  if(!link)return;
  const row=document.createElement('div');row.className='outline-row';li.insertBefore(row,link);row.append(link);
  if(child){
   const button=document.createElement('button');button.type='button';button.className='outline-branch';button.textContent='▾';
   button.setAttribute('aria-label','展开或折叠：'+link.textContent);button.setAttribute('aria-expanded','true');
   const set=open=>{child.hidden=!open;button.setAttribute('aria-expanded',String(open));button.textContent=open?'▾':'▸'};
   button.addEventListener('click',()=>set(child.hidden));row.prepend(button);buttons.push({set,child});
  }else row.classList.add('outline-leaf');
 });
 document.querySelectorAll('[data-outline-action]').forEach(b=>b.addEventListener('click',()=>buttons.forEach(x=>x.set(b.dataset.outlineAction==='expand'))));
 const links=[...tree.querySelectorAll('a[href^="#"]')];
 const items=links.map(a=>{let id;try{id=decodeURIComponent(a.hash.slice(1))}catch{id=a.hash.slice(1)}return {a,heading:document.getElementById(id)}}).filter(x=>x.heading);
 function mark(item){items.forEach(x=>{x.a.classList.toggle('is-active',x===item);if(x===item)x.a.setAttribute('aria-current','location');else x.a.removeAttribute('aria-current')})}
 let queued=false;
 function update(){queued=false;let current=items[0];for(const item of items){if(item.heading.getBoundingClientRect().top<=140)current=item;else break}if(current)mark(current)}
 addEventListener('scroll',()=>{if(!queued){queued=true;requestAnimationFrame(update)}},{passive:true});
 links.forEach(a=>a.addEventListener('click',()=>{const item=items.find(x=>x.a===a);if(item)mark(item);if(matchMedia('(max-width: 1000px)').matches)panel.open=false}));
 if(matchMedia('(max-width: 1000px)').matches)panel.open=false;
 update();
})();
