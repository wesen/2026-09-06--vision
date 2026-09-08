// Small explicit Cartesian plans, persisted before any inference begins.
const batchPanel=node('section',undefined,'panel');batchPanel.id='batchPanel';
batchPanel.append(node('h2','Controlled experiment batches'));
const batchName=node('input');batchName.id='batchName';batchName.value='Matched experiment comparison';
const batchModels=node('select');batchModels.id='batchModels';batchModels.append(new Option('Current model only','current'),new Option('Qwen + Cosmos (reasoning/states)','reasoners'),new Option('Pooled + native (embeddings)','embeddings'));
const batchCrops=node('select');batchCrops.id='batchCrops';batchCrops.append(new Option('Current crop only','current'),new Option('Current crop + full frame','both'));
const batchPrompt=node('textarea');batchPrompt.id='batchPrompt';batchPrompt.rows=4;batchPrompt.maxLength=16000;batchPrompt.placeholder='Optional second complete user prompt; leave empty for the current prompt only.';
for(const [text,control] of [['Batch name',batchName],['Model variants',batchModels],['Crop variants',batchCrops],['Additional prompt variant (reasoning/states only)',batchPrompt]]){const label=node('label',text);label.append(control);batchPanel.append(label)}
const previewBatch=node('button','Preview batch plan');previewBatch.id='previewBatch';
const startBatch=node('button','Start previewed batch');startBatch.id='startBatch';startBatch.disabled=true;
const cancelBatch=node('button','Cancel active batch');cancelBatch.id='cancelBatch';cancelBatch.disabled=true;
const batchStatus=node('p');batchStatus.setAttribute('role','status');const batchResults=node('div');batchResults.id='batchResults';
const batchHistory=node('select');batchHistory.id='batchHistory';batchHistory.setAttribute('aria-label','Saved batch');
batchPanel.append(previewBatch,startBatch,cancelBatch,batchStatus,batchHistory,batchResults);
batchPanel.append(node('p','The current experiment form supplies source, time range, FPS and fixed settings. Preview expands 2–8 explicit children, decodes their inputs and freezes prompt text. Start runs that saved plan even if you later edit the form. Children run sequentially with their existing deadlines; one failure is recorded and later children continue. Cancel stops the active child and skips remaining children. This reserves the lab worker, not unrelated programs on the Mac.','muted'));
batchPanel.append(node('p','A full-frame variant explicitly detaches any detector-crop binding. Crop changes are input interventions. Default prompts can differ by model/profile: inspect the expanded plan before calling a result a model-only comparison. Summaries report model outputs and failures, not accuracy without independent review. The displayed maximum is the sum of worker deadlines; decoding and preparation add overhead.','muted'));
$('history').after(batchPanel);
const batchShortcut=node('a','Plan a comparison batch ↓');batchShortcut.href='#batchPanel';$('runStatus').after(batchShortcut);
let currentBatch=null,batchPoll=null,batchGeneration=0;
function batchPlanFromForm(){
    const base=experiment();let models=[base.model];
    if(batchModels.value==='reasoners'){if(!['reasoning','states'].includes(base.component))throw Error('Select reasoning or states for Qwen/Cosmos');models=['qwen','cosmos']}
    if(batchModels.value==='embeddings'){if(base.component!=='embeddings')throw Error('Select embeddings for pooled/native');models=['pooled_images','native_video']}
    const crops=[{label:'selected input',crop:base.crop,handoff:base.handoff||null}];
    if(batchCrops.value==='both'){if(!base.crop)throw Error('Select a crop first; current input is already full frame');crops.push({label:'full frame',crop:null,handoff:null})}
    const prompts=[{label:'current prompt',prompt:base.prompt||null}];
    if(batchPrompt.value.trim()){if(!['reasoning','states'].includes(base.component))throw Error('Prompt variants require reasoning or states');prompts.push({label:'alternate prompt',prompt:batchPrompt.value})}
    const entries=[];for(const model of models)for(const crop of crops)for(const prompt of prompts)entries.push({label:`${model} · ${crop.label} · ${prompt.label}`,options:{...base,model,crop:crop.crop,handoff:crop.handoff,prompt:prompt.prompt}});
    if(entries.length<2||entries.length>8)throw Error('Choose 2–8 variants; add a model, crop or prompt comparison');
    return {name:batchName.value,entries};
}
async function refreshBatchHistory(){const result=await api('/v1/lab/batches');batchHistory.replaceChildren(new Option('Open a saved batch',''),...result.batches.map(b=>new Option(`${b.request.name} · ${b.status} · ${b.batch_id}`,b.batch_id)));if(currentBatch)batchHistory.value=currentBatch}
function renderBatch(value){
    currentBatch=value.batch_id;startBatch.disabled=value.status!=='draft';cancelBatch.disabled=value.status!=='running';
    const counts={};for(const c of value.children)counts[c.status]=(counts[c.status]||0)+1;
    batchStatus.textContent=`${value.request.name} · ${value.status} · ${Object.entries(counts).map(([k,v])=>v+' '+k).join(', ')} · worker deadline sum ${value.request.maximum_worker_seconds} s`;
    batchResults.replaceChildren();
    const table=node('table');const header=node('tr');['Variant','Status / time','Outputs','Inspect'].forEach(t=>header.append(node('th',t)));table.append(header);
    value.children.forEach((child,i)=>{
        const entry=value.request.entries[i],row=node('tr');row.append(node('td',entry.label),node('td',`${child.status}${child.elapsed_seconds!=null?' · '+child.elapsed_seconds.toFixed(2)+' s':''}`));
        const outcomes=child.outcomes?.map(o=>`${o.pts_us/1e6} s: ${o.state?o.state+' / '+o.validation:o.detections+' detections'}`).join('; ')||child.action_predictions?.join(', ')||(child.top_window?`top ${child.top_window.start_us/1e6}–${child.top_window.end_us/1e6} s: ${child.top_window.score.toFixed(4)}`:'');
        row.append(node('td',child.error||outcomes||'—'));const inspect=node('td');
        if(child.run_id){const open=node('button','Open run');open.onclick=()=>{openRun(child.run_id);document.querySelector('[data-tab="results"]').click()};inspect.append(open);const first=value.children.find(c=>c.run_id);if(first&&first.run_id!==child.run_id){const link=node('a','Compare with first');link.href=`/?tab=history&a=${first.run_id}&b=${child.run_id}&compare=1`;link.target='_blank';inspect.append(link)}}
        row.append(inspect);table.append(row);
    });batchResults.append(table);
    const plans=node('details');plans.open=value.status==='draft';plans.append(node('summary','Frozen child inputs and options'));
    for(const entry of value.request.entries){const section=node('article');section.append(node('h3',entry.label));const frames=node('div',undefined,'samples');for(const frame of entry.evidence.frames){const img=node('img');img.src=artifactUrl(entry.preview_id,frame.file);img.alt=`${entry.label} at ${frame.pts_us/1e6} s`;img.title=`${frame.pts_us/1e6} s · crop ${frame.crop_xyxy}`;frames.append(img)}section.append(frames,jsonDetails('Frozen options YAML',entry.options));plans.append(section)}
    batchResults.append(plans,jsonDetails('Batch record YAML',value));
    const exportLink=node('a','Export batch manifest and summary');exportLink.href='/v1/lab/batches/'+value.batch_id;exportLink.target='_blank';batchResults.append(exportLink);
}
async function openBatch(id){const generation=++batchGeneration;clearTimeout(batchPoll);try{const value=await api('/v1/lab/batches/'+id);if(generation!==batchGeneration)return;renderBatch(value);if(value.status==='running')batchPoll=setTimeout(()=>openBatch(id),1000);else {refreshBatchHistory();refreshHistory()}}catch(error){batchStatus.textContent=error.message}}
previewBatch.onclick=async()=>{previewBatch.disabled=true;try{const value=await api('/v1/lab/batches/preview',batchPlanFromForm());++batchGeneration;clearTimeout(batchPoll);renderBatch(value);await refreshBatchHistory()}catch(error){batchStatus.textContent=error.message}finally{previewBatch.disabled=false}};
startBatch.onclick=async()=>{startBatch.disabled=true;try{await api('/v1/lab/batches/'+currentBatch+'/start',{});await openBatch(currentBatch)}catch(error){batchStatus.textContent=error.message;startBatch.disabled=false}};
cancelBatch.onclick=async()=>{try{await api('/v1/lab/batches/'+currentBatch+'/cancel',{});await openBatch(currentBatch)}catch(error){batchStatus.textContent=error.message}};
batchHistory.onchange=()=>{if(batchHistory.value)openBatch(batchHistory.value)};
refreshBatchHistory().catch(error=>batchStatus.textContent=error.message);
