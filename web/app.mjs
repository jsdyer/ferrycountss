import {profile} from "./model.mjs";
const el = id => document.getElementById(id);
const create = (tag,content,cls) => {
  const n=document.createElement(tag);
  if(content!=null)n.textContent=content;
  if(cls)n.className=cls;
  return n;
};
const fmt = n => n.toLocaleString("en-CA",{maximumFractionDigits:1});
const clock = h => String(h).padStart(2,"0")+":00";
const read = async path => { const r=await fetch("./data/"+path+".json"); if(!r.ok)throw Error("Missing data");return r.json(); };
try {
  const [status,cells] = await Promise.all([read("status"),read("profile")]);
  el("edition").textContent=status.start+" to "+status.end+" · "+fmt(status.records)+" reported records · Retrieved "+status.retrieved;
  for(const [id,label] of Object.entries(status.routes)){
    for(const control of ["route","comparison"])el(control).add(new Option(label,id));
  }
  el("route").value="FerryHD";el("comparison").value="FerryDH";
  for(const period of [...new Set(cells.map(r=>r[1]))].sort().reverse())el("month").add(new Option(period,period));
  ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].forEach((x,i)=>el("weekday").add(new Option(x,i)));
  let current;
  function render(){
    const ids=[el("route").value,el("comparison").value], names=ids.map(k=>status.routes[k]);
    const results=ids.map(id=>profile(cells,id,el("weekday").value,el("month").value));
    current={results,names};
    el("legend").replaceChildren(...names.map(n=>create("span",n)));
    el("a-col").textContent=names[0];el("b-col").textContent=names[1];
    const max=Math.max(1,...results.flat().map(r=>r.mean||0));
    const peaks=results.map(series=>series.filter(r=>r.days).sort((a,b)=>b.mean-a.mean)[0]);
    el("finding").textContent=names.map((n,i)=>peaks[i]?n+" peaked at "+clock(peaks[i].hour)+" ("+fmt(peaks[i].mean)+" boardings per observed hour).":n+" has no records for this selection.").join(" ");
    const bars=[],table=[];
    for(let h=0;h<24;h++){
      const pair=results.map(s=>s[h]),tr=create("tr");tr.append(create("th",clock(h)));
      for(const r of pair)tr.append(create("td",r.days?fmt(r.mean)+" avg · "+fmt(r.total)+" total · "+r.days+" dates":"No observations"));
      table.push(tr);
      if(!pair.some(r=>r.days))continue;
      const row=create("div",null,"hour"), tracks=create("div",null,"tracks");row.append(create("span",clock(h)),tracks);
      for (const r of pair){
        const track=create("div",null,"track"),bar=create("span",null,"bar");
        bar.style.width=(r.mean||0)/max*82+"%";
        track.append(bar,create("span",r.days?fmt(r.mean):"—","small"));tracks.append(track);
      }
      bars.push(row);
    }
    el("chart").replaceChildren(...(bars.length?bars:[create("p","No observations for these directions and days.")]));
    el("rows").replaceChildren(...table);
  }
  for(const id of ["route","comparison","month","weekday"])el(id).addEventListener("change",render);
  el("download").addEventListener("click",()=>{
    const lines=["direction,month,days,hour,boardings,observed_dates,mean_boardings"];
    current.results.forEach((series,i)=>series.forEach(r=>lines.push([current.names[i],el("month").value,el("weekday").selectedOptions[0].text,clock(r.hour),r.days?r.total:"",r.days,r.days?r.mean.toFixed(2):""].join(","))));
    const a=create("a");a.href=URL.createObjectURL(new Blob([lines.join("\r\n")],{type:"text/csv;charset=utf-8"}));a.download="halifax-ferry-counts.csv";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
  });render();
} catch {el("edition").textContent="The boarding records could not load. Reload the page or open the Halifax Transit source below.";}
