// Comparisons and reviews always bind saved run IDs, never current form values.
let historyRuns=[];
let comparisonUrlReady=false, restoringComparisonUrl=false, comparisonRequestGeneration=0;
const comparisonParams={historyPreset:'history_preset',historyComponent:'history_component',historyModel:'history_model',compareA:'a',compareB:'b'};
function saveComparisonUrl(rendered=false) {
    if(!comparisonUrlReady || restoringComparisonUrl)return;
    const url=new URL(location.href);
    url.searchParams.set('tab',document.querySelector('[data-tab].active')?.dataset.tab||'history');
    for(const [id,param] of Object.entries(comparisonParams)) {
        if($(id).value)url.searchParams.set(param,$(id).value);else url.searchParams.delete(param);
    }
    if(rendered)url.searchParams.set('compare','1');else url.searchParams.delete('compare');
    if(url.href!==location.href)history.pushState(null,'',url);
    $('comparisonLink').href=url.href;
}
function clearComparison() {
    comparisonRequestGeneration++;
    $('comparison').replaceChildren();
}

const experimentPresets = {
    masks: {component:'segmentation',model:'yolo11n-seg',fps:2},
    point: {component:'reasoning',model:'qwen',fps:1},
    states: {component:'states',model:'qwen',fps:1},
    native: {component:'embeddings',model:'native_video',fps:2}
};
function matchingHistory() {
    const preset=experimentPresets[$('historyPreset').value];
    return historyRuns.filter(run => {
        const options=run.request.options;
        return (!$('historyComponent').value || options.component===$('historyComponent').value)
            && (!$('historyModel').value || options.model===$('historyModel').value)
            && (!preset || Object.entries(preset).every(([key,value])=>options[key]===value));
    });
}
function renderHistory() {
    const filtered=matchingHistory(), body=$('historyBody');
    $('historyCount').textContent=`${filtered.length} of ${historyRuns.length} saved experiments`;
    body.replaceChildren();
    for(const run of filtered) {
        const options=run.request.options;
        const button=node('button',`${run.status} · ${options.component} / ${names[options.model]||options.model} · ${options.episode_id} · ${options.start_us/1e6}–${options.end_us/1e6} s · ${run.run_id}`,'history-run');
        button.dataset.runId=run.run_id;
        button.onclick=()=>{openRun(run.run_id);document.querySelector('[data-tab="results"]').click()};
        body.append(button);
    }
    if(!filtered.length)body.append(node('p','No experiments match these filters. Clear a filter or choose another combination.','muted'));
    for(const id of ['compareA','compareB']) {
        const previous=$(id).value;
        $(id).replaceChildren(...filtered.map(run=>new Option(`${run.request.options.component} / ${run.request.options.model} · ${run.run_id}`,run.run_id)));
        if(filtered.some(run=>run.run_id===previous))$(id).value=previous;
    }
    if($('compareA').value===$('compareB').value && filtered.length>1)$('compareB').selectedIndex=1;
    $('compareButton').disabled=filtered.length<2;
}
let historyGeneration=0;
async function refreshHistory(restore=false) {
    const generation=++historyGeneration;
    try {
        const data=await api('/v1/lab/runs');
        if(generation!==historyGeneration)return;
        historyRuns=data.runs;
        // A shared comparison can refer to runs outside the recent-history page.
        const params=new URLSearchParams(location.search);
        const missing=[...new Set(['a','b'].map(key=>params.get(key)).filter(Boolean))].filter(id=>!historyRuns.some(r=>r.run_id===id));
        for(const id of missing) {
            if(!/^run-[a-f0-9]{16}$/.test(id))throw Error('Invalid run ID in comparison URL');
            const run=await api('/v1/lab/runs/'+id);
            if(generation!==historyGeneration)return;
            historyRuns.push(run);
        }
        for(const [id,key] of [['historyComponent','component'],['historyModel','model']]) {
            const previous=$(id).value;
            $(id).replaceChildren(new Option(key==='model'?'All models':'All components',''),
                ...[...new Set(historyRuns.map(run=>run.request.options[key]))].sort().map(value=>new Option(key==='model'?(names[value]||value):value,value)));
            $(id).value=previous;
        }
        renderHistory();
        if(!comparisonUrlReady || restore) {
            restoringComparisonUrl=true;
            try {
                $('error').textContent='';
                clearComparison();
                for(const id of ['historyPreset','historyComponent','historyModel']) {
                    const value=params.get(comparisonParams[id])||'';
                    if(![...$(id).options].some(o=>o.value===value))throw Error('Unknown filter in comparison URL: '+comparisonParams[id]);
                    $(id).value=value;
                }
                renderHistory();
                for(const id of ['compareA','compareB']) {
                    const value=params.get(comparisonParams[id]);
                    if(value) {
                        if(![...$(id).options].some(o=>o.value===value))throw Error('Linked run is excluded by the URL filters: '+value);
                        $(id).value=value;
                    }
                }
                const tab=params.get('tab')||(params.has('a')||params.has('b')?'history':'results');
                if(['results','guide','history'].includes(tab))document.querySelector('[data-tab="'+tab+'"]').click();
                comparisonUrlReady=true;
                $('comparisonLink').href=location.href;
                if(params.get('compare')==='1') {
                    if(!params.get('a')||!params.get('b'))throw Error('Comparison URL requires both run IDs');
                    await $('compareButton').onclick();
                }
            }finally{restoringComparisonUrl=false;comparisonUrlReady=true;}
        }
    }catch(error){comparisonUrlReady=true;fail(error)}
}
for(const id of ['historyPreset','historyComponent','historyModel'])$(id).onchange=()=>{clearComparison();renderHistory();saveComparisonUrl()};
$('clearHistoryFilters').onclick=()=>{for(const id of ['historyPreset','historyComponent','historyModel'])$(id).value='';clearComparison();renderHistory();saveComparisonUrl()};
function addSimilarityPlot(container, series, comparison=false) {
    const ns='http://www.w3.org/2000/svg';
    const all=series.flatMap(s=>s.windows);
    if(!all.length)return;
    const colors=['#a5ebc8','#ffbf80'];
    const lo=Math.min(...all.map(w=>w.score))-.02;
    const hi=Math.max(...all.map(w=>w.score))+.02;
    const t0=Math.min(...all.map(w=>w.start_us));
    const t1=Math.max(...all.map(w=>w.end_us));
    const x=t=>75+(t-t0)/Math.max(1,t1-t0)*720;
    const y=value=>220-(value-lo)/(hi-lo)*170;
    function element(tag,attributes={},text) {
        const e=document.createElementNS(ns,tag);
        for(const [key,value] of Object.entries(attributes))e.setAttribute(key,String(value));
        if(text!==undefined)e.textContent=text;
        return e;
    }
    const svg=element('svg',{viewBox:'0 0 850 290',role:'img','aria-label':comparison?'Embedding comparison with shared time and cosine similarity axes':'Cosine similarity over source time'});
    svg.style.width='100%';
    svg.append(element('text',{x:75,y:24,fill:'#a4b6b4'},'Cosine similarity'));
    for(let i=0;i<5;i++) {
        const value=lo+(hi-lo)*i/4;
        svg.append(element('line',{x1:75,x2:795,y1:y(value),y2:y(value),stroke:'#334449'}));
        svg.append(element('text',{x:65,y:y(value)+5,fill:'#a4b6b4','text-anchor':'end'},value.toFixed(3)));
        const time=t0+(t1-t0)*i/4;
        svg.append(element('text',{x:x(time),y:246,fill:'#a4b6b4','text-anchor':'middle'},(time/1e6).toFixed(2)));
    }
    svg.append(element('text',{x:435,y:276,fill:'#a4b6b4','text-anchor':'middle'},'Source time (seconds)'));
    const legend=node('div',undefined,'chips');
    series.forEach((s,index)=>{
        const color=colors[index%colors.length];
        const label=node('span',`${index?'┄':'━'} ${s.label}`,'chip');
        label.style.color=color;legend.append(label);
        const windows=[...s.windows].sort((a,b)=>a.start_us-b.start_us);
        const attributes={points:windows.map(w=>`${x(w.start_us)},${y(w.score)}`).join(' '),fill:'none',stroke:color,'stroke-width':3};
        if(index)attributes['stroke-dasharray']='8 5';
        svg.append(element('polyline',attributes));
        for(const w of windows) {
            const dot=element('circle',{cx:x(w.start_us),cy:y(w.score),r:index?4:5,fill:color,stroke:'#101619','stroke-width':1});
            dot.append(element('title',{},`${s.label} · ${w.start_us/1e6}–${w.end_us/1e6} s · cosine ${w.score.toFixed(4)}`));
            svg.append(dot);
        }
    });
    container.append(legend,svg,node('p',comparison
        ? 'Both curves use the same time and similarity scales, calculated from all displayed windows. Points mark window starts; hover for the run, interval and score. Shared axes do not calibrate different feature spaces.'
        : 'Points mark window starts; hover for exact values. Similarity is not probability.','muted'));
}
function addPlot(container,windows){addSimilarityPlot(container,[{label:'Window similarity',windows}])}
const oldRenderResult=renderResult;
renderResult=function(record){oldRenderResult(record);const body=$('resultBody');if(record.result?.windows)addPlot(body,record.result.windows);if(record.result?.action_windows){body.append(node('h3','Fresh action predictions'),node('p',record.result.scope));const table=node('table');for(const row of record.result.action_windows){const tr=node('tr');[`${row.start_us/1e6}–${row.end_us/1e6} s`,row.prediction,'PTS '+row.pts_us.map(t=>t/1e6).join(', ')].forEach(x=>tr.append(node('td',x)));table.append(tr)}body.append(table)}if(record.status==='completed'){const panel=node('div');panel.append(node('h3','Review this saved experiment'));const verdict=node('select');['correct','incorrect','unjudgeable'].forEach(v=>verdict.append(new Option(v,v)));verdict.value='unjudgeable';const note=node('textarea');note.placeholder='Describe the visual evidence and what was right, wrong, or impossible to judge.';note.setAttribute('aria-label','Review explanation');const save=node('button','Save independent review'),status=node('p');save.onclick=async()=>{try{const result=await api('/v1/lab/runs/'+record.run_id+'/reviews',{verdict:verdict.value,note:note.value});status.textContent='Saved '+result.review_id+' · source partition '+result.source.split}catch(e){status.textContent=e.message}};const exp=node('a','Export experiment and reviews');exp.href='/v1/lab/runs/'+record.run_id+'/export';exp.target='_blank';panel.append(verdict,note,save,status,exp,node('p','Reviews are separate annotations. Predictions stay unchanged; exported cases retain their source partition.','muted'));body.append(panel);if(['reasoning','states'].includes(record.result?.kind)){const box=node('details');box.open=true;box.append(node('summary','Evaluate a rule using these exact state samples'));const t=node('input');t.type='number';t.step='.1';t.value=record.request.options.start_us/1e6;const label=node('label','User-selected trigger time (source seconds)');label.append(t);const expected=node('select');expected.append(new Option('Door must be closed','false'),new Option('Door must be open','true'));const run=node('button','Evaluate exact-point rule'),out=node('div');run.onclick=async()=>{try{const r=await api('/v1/lab/runs/'+record.run_id+'/rule',{event_us:Math.round(Number(t.value)*1e6),expected_open:expected.value==='true'});out.replaceChildren(node('h3',r.decision.status),node('p',r.decision.reason),node('p',r.scope),jsonDetails('Rule and supporting evidence',r))}catch(e){out.textContent=e.message}};box.append(node('p','This is a manually selected point, not a detected departure. A known matching state gives PASS, a contradiction gives VIOLATION, and no exact sample gives UNKNOWN. Nearby samples are not substituted.'),label,expected,run,out);body.append(box)}}};
$('compareButton').onclick=async()=>{const generation=++comparisonRequestGeneration;try{const a=$('compareA').value,b=$('compareB').value;if(!a||!b)throw Error('Choose two saved runs');saveComparisonUrl(true);const report=await api('/v1/lab/compare?a='+a+'&b='+b),records=await Promise.all([api('/v1/lab/runs/'+a),api('/v1/lab/runs/'+b)]),body=$('comparison');if(generation!==comparisonRequestGeneration)return;body.replaceChildren(node('h3',report.same_evidence?'Matched visual evidence':'Different visual evidence'),node('p',report.interpretation));if(report.feature_note)body.append(node('p',report.feature_note));const table=node('table');for(const d of report.differences){const tr=node('tr');tr.append(node('td',d.field));for(const [label,value] of [['Run A',d.a],['Run B',d.b]]){const cell=node('td');cell.append(jsonDetails(label,value));tr.append(cell)}table.append(tr)}body.append(table);const embeddingSeries=records.map((r,i)=>r.result?.windows?.length?{label:`${i?'B':'A'} · ${r.request.options.model} · ${r.run_id}`,windows:r.result.windows}:null).filter(Boolean);if(embeddingSeries.length){body.append(node('h3','Embedding similarity overlay'));addSimilarityPlot(body,embeddingSeries,true)}const grid=node('div',undefined,'result-grid');for(const r of records){const col=node('article');col.append(node('h3',r.request.options.model+' · '+r.status));for(const row of r.result?.records||[]){const img=node('img');img.src=artifactUrl(r.run_id,row.overlay||row.frame.file);img.alt='Comparison evidence';col.append(img,node('p',`${row.frame.pts_us/1e6} s · ${row.state||row.detections.length+' detections'}`));if(row.parsed)col.append(node('p',row.parsed.answer?.rationale||row.parsed.reason||''))}if(r.result?.action_windows){for(const w of r.result.action_windows)col.append(node('p',`${w.start_us/1e6}–${w.end_us/1e6} s · ${w.prediction}`))}if(r.result?.windows){for(const i of r.result.ranking){const w=r.result.windows[i];col.append(node('p',`${w.start_us/1e6}–${w.end_us/1e6} s · ${w.score.toFixed(4)}`))}}grid.append(col)}body.append(grid,jsonDetails('Comparison contract',report))}catch(e){if(generation===comparisonRequestGeneration)fail(e)}};
$('inspectActions').onclick=async()=>{try{const r=await api('/v1/lab/actions/inspect',selection()),out=$('actionResults');out.replaceChildren(node('p',r.scope||r.reason));if(r.records.length){const table=node('table'),head=node('tr');['Saved model','Window (s)','Prediction','Actual PTS'].forEach(x=>head.append(node('th',x)));table.append(head);for(const row of r.records){const tr=node('tr');[row.model,`${row.start_us/1e6}–${row.end_us/1e6}`,row.prediction,row.pts_us.map(x=>x/1e6).join(', ')].forEach(x=>tr.append(node('td',x)));table.append(tr)}out.append(table)}out.append(jsonDetails('Frozen action provenance',r))}catch(e){fail(e)}};
$('preset').onchange=()=>{const value=$('preset').value;if(!value)return;const p=experimentPresets[value];$('component').value=p.component;componentChanged();$('model').value=p.model;$('fps').value=p.fps;if(value==='point')$('end').value=(Number($('start').value)+.1).toFixed(3);modelChanged();$('previewStatus').textContent='Preset applied. Preview the changed selection before running.'};
for(const id of ['compareA','compareB'])$(id).onchange=()=>{clearComparison();saveComparisonUrl()};
window.addEventListener('popstate',()=>{clearComparison();refreshHistory(true)});
document.querySelectorAll('[data-tab]').forEach(button=>button.addEventListener('click',()=>{
    if(!comparisonUrlReady||restoringComparisonUrl)return;
    const url=new URL(location.href);url.searchParams.set('tab',button.dataset.tab);
    if(url.href!==location.href)history.pushState(null,'',url);
}));
refreshHistory();

// A saved result has its own player. Seeking it never relabels the editable form.
async function loadRunSettings(record) {
    const options = record.request.options;
    $('source').value = options.episode_id;
    await sourceChanged();
    if (source?.episode_id !== options.episode_id) throw Error('Could not load the saved source');
    $('component').value = options.component;
    componentChanged();
    for (const [key, value] of Object.entries(options)) {
        if (!$(key) || ['episode_id', 'crop', 'component'].includes(key)) continue;
        $(key).value = key === 'classes' ? value.join(',') : String(value);
    }
    $('start').value = options.start_us / 1e6;
    $('end').value = options.end_us / 1e6;
    (options.crop || [0, 0, 1, 1]).forEach((v, i) => $(['x0', 'y0', 'x1', 'y1'][i]).value = v);
    $('preset').value = '';
    modelChanged();
    await previewInputs();
    $('runStatus').textContent = 'Settings loaded from ' + record.run_id + '. Edit options and run to create a new experiment.';
    $('source').scrollIntoView({behavior: 'smooth', block: 'center'});
}

function resultTimeline(record) {
    const options = record.request.options, result = record.result || {};
    const panel = node('section', undefined, 'saved-timeline');
    panel.append(node('h3', 'Explore this saved run in time'));
    const load = node('button', 'Load settings to modify and rerun');
    load.onclick = () => loadRunSettings(record).catch(fail);
    panel.append(load, node('p', 'Click an input or output below to seek this run’s video. The player and evidence are bound to the saved recording; your experiment form stays unchanged.', 'muted'));
    const media = node('div', undefined, 'result-grid');
    const player = node('video');
    player.controls = true;
    player.preload = 'metadata';
    player.src = '/v1/lab/sources/' + encodeURIComponent(options.episode_id) + '/video';
    player.style.maxHeight = '280px';
    const evidence = node('div'), image = node('img'), caption = node('p');
    image.style.maxHeight = '280px'; image.style.objectFit = 'contain';
    evidence.append(image, caption); media.append(player, evidence); panel.append(media);
    const clock = node('p', 'Source time —', 'muted'); panel.append(clock);
    const frames = record.request.evidence.frames;
    function show(item) {
        const frame = frames.find(f => f.id === item.frameId) || frames.find(f => f.pts_us >= item.start && f.pts_us < item.end);
        const seek = () => { player.currentTime = item.start / 1e6; };
        if (player.readyState >= 1) seek(); else player.addEventListener('loadedmetadata', seek, {once: true});
        if (frame) {
            const row = result.records?.find(r => r.frame.id === frame.id);
            image.src = artifactUrl(record.run_id, row?.overlay || frame.file);
            image.alt = 'Saved evidence at ' + frame.pts_us / 1e6 + ' seconds';
            caption.textContent = `${item.label} · displayed exact frame ${(frame.pts_us / 1e6).toFixed(3)} s`;
            image.hidden = false;
        } else {
            image.hidden = true; caption.textContent = item.label + ' · no sampled image in this interval';
        }
    }
    const scrub = node('input'); scrub.type = 'range'; scrub.min = options.start_us / 1e6;
    scrub.max = options.end_us / 1e6; scrub.step = '.01'; scrub.value = scrub.min;
    scrub.setAttribute('aria-label', 'Seek within saved run range');
    scrub.oninput = () => { player.currentTime = Number(scrub.value); };
    player.addEventListener('timeupdate', () => {
        clock.textContent = `Source time ${player.currentTime.toFixed(3)} s · saved selection ${options.start_us / 1e6}–${options.end_us / 1e6} s`;
        scrub.value = player.currentTime;
    });
    panel.append(scrub);
    const lanes = [{title: 'Exact inputs', items: frames.map(f => ({start: f.pts_us, end: f.pts_us, frameId: f.id, label: `#${f.frame_index} · ${(f.pts_us / 1e6).toFixed(2)} s`}))}];
    if (result.records?.some(r => r.state)) lanes.push({title: 'Point states', items: result.records.map(r => ({start: r.pts_us, end: r.pts_us, frameId: r.frame.id, label: r.state.toUpperCase()}))});
    if (result.records?.some(r => r.detections)) lanes.push({title: 'Detections / tracks', items: result.records.map(r => ({start: r.frame.pts_us, end: r.frame.pts_us, frameId: r.frame.id, label: `${r.detections.length} boxes · ${r.tracks.length} tracks`}))});
    if (result.events?.length) lanes.push({title: 'Transition uncertainty', items: result.events.map(e => ({start: e.start_us, end: e.end_us, frameId: e.evidence_ids[1], label: e.kind + ' (start, end]'}))});
    if (result.action_windows) lanes.push({title: 'Action windows', items: result.action_windows.map(w => ({start: w.start_us, end: w.end_us, frameId: w.frame_ids.at(-1), label: w.prediction}))});
    if (result.windows) lanes.push({title: 'Embedding windows', items: result.windows.map(w => ({start: w.start_us, end: w.end_us, frameId: w.frame_ids[0], label: 'cosine ' + w.score.toFixed(3)}))});
    for (const lane of lanes) {
        panel.append(node('h4', lane.title));
        const scale=node('div',undefined,'time-scale');scale.append(node('span', options.start_us/1e6+' s'),node('span',options.end_us/1e6+' s'));panel.append(scale);
        const track = node('div', undefined, 'time-lane');
        // Overlapping intervals occupy separate rows; no inferred duration for point samples.
        const ends = [];
        for (const item of lane.items) {
            let row = ends.findIndex(end => end <= item.start);
            if (row < 0) row = ends.length;
            const visualEnd = Math.max(item.end, item.start + (options.end_us - options.start_us) * .13);
            ends[row] = visualEnd;
            const button = node('button', item.label, 'time-item');
            const span = options.end_us - options.start_us;
            button.style.left = ((item.start - options.start_us) / span * 100) + '%';
            button.style.width = Math.max(12, (item.end - item.start) / span * 100) + '%';
            if (item.end === item.start) button.style.transform = 'translateX(-50%)';
            button.style.top = (row * 34) + 'px';
            button.title = item.end === item.start ? `Point at ${item.start / 1e6} s` : `${item.start / 1e6}–${item.end / 1e6} s`;
            button.onclick = () => show(item); track.append(button);
        }
        track.style.height = Math.max(1, ends.length) * 34 + 'px'; panel.append(track);
    }
    const help = node('details'); help.append(node('summary', 'Guide: reading points, intervals and windows'), node('p', 'Point samples describe only their exact timestamps; button width does not imply state duration. Action and embedding bars span their input windows. Transition intervals express uncertainty between two state samples. The displayed PNG is a specific saved frame, whose timestamp is printed below it; playback does not generate new predictions.'));
    panel.append(help);
    if (frames.length) show({start: frames[0].pts_us, end: frames[0].pts_us + 1, frameId: frames[0].id, label: 'Initial saved input'});
    return panel;
}
const renderWithoutTimeline = renderResult;
renderResult = function(record) {
    renderWithoutTimeline(record);
    if (record.status === 'completed') $('resultBody').prepend(resultTimeline(record));
};

// Explicit detector-to-reasoner drafts. Evidence edits require deliberate detachment.
let reasoningHandoff = null;
const handoffNotice = node('div'); handoffNotice.id = 'handoffNotice';
$('runStatus').before(handoffNotice);
function setHandoff(binding) {
    reasoningHandoff = binding;
    handoffNotice.replaceChildren();
    if (!binding) return;
    const detach = node('button', 'Detach detection provenance to edit evidence');
    detach.onclick = () => setHandoff(null);
    handoffNotice.append(node('p', `Bound detection draft: ${binding.run_id} / ${binding.frame_id}. Model and decoding settings may change; source, time, crop and target must stay fixed.`), detach);
}
const experimentWithoutHandoff = experiment;
experiment = function() {
    const options = experimentWithoutHandoff();
    if (reasoningHandoff) options.handoff = reasoningHandoff;
    return options;
};
const loadWithoutHandoff = loadRunSettings;
loadRunSettings = async function(record) {
    setHandoff(null);
    await loadWithoutHandoff(record);
    setHandoff(record.request.options.handoff || null);
};
function detectionHandoffPanel(record) {
    const panel = node('section'); panel.id = 'detectionHandoff';
    panel.append(node('h3', 'Use a detection for door-state reasoning'));
    const choices = [];
    for (const row of record.result.records || []) for (const detection of row.detections || []) {
        if (['refrigerator', 'microwave', 'oven'].includes(detection.class_name)) choices.push({row, detection});
    }
    panel.append(node('p', 'Choose an actual detected appliance and preview a crop at its exact timestamp. This prepares a single-image Qwen or Cosmos experiment; it does not run inference until you press Run experiment. A box identifies a region, not whether its door is open.'));
    if (!choices.length) { panel.append(node('p', 'No supported door-bearing appliance detections in this run. Try another range or detection threshold.')); return panel; }
    const select = node('select'); select.id = 'handoffDetection';
    choices.forEach(({row, detection}, i) => select.append(new Option(`${row.frame.pts_us/1e6} s · ${detection.class_name} · score ${detection.score.toFixed(3)} · ${detection.detection_id}`, i)));
    const padding = node('input'); padding.type = 'number'; padding.min = '0'; padding.max = '1'; padding.step = '.05'; padding.value = '.15'; padding.id = 'handoffPadding';
    const label = node('label', 'Context padding per side (fraction of box width / height)'); label.append(padding);
    const button = node('button', 'Preview reasoning draft'); button.id = 'prepareHandoff';
    const status = node('p');
    button.onclick = async () => {
        button.disabled = true;
        try {
            const {row, detection} = choices[Number(select.value)];
            const draft = await api('/v1/lab/handoff', {run_id:record.run_id, frame_id:row.frame.id, detection_id:detection.detection_id, padding:Number(padding.value)});
            await loadRunSettings({run_id:record.run_id, request:{options:draft.options}});
            status.textContent = 'Draft prepared; inspect the exact crop above, choose Qwen or Cosmos, then Run experiment.';
            $('runStatus').textContent = status.textContent;
        } catch (error) { status.textContent = error.message; }
        finally { button.disabled = false; }
    };
    const guide = node('details'); guide.append(node('summary', 'Guide: crop coordinates, context and provenance'), node('p', 'For box (x0,y0,x1,y1), padding p adds p×(x1−x0) horizontally and p×(y1−y0) vertically on each side. The server adds the parent crop origin, rounds outward to pixels and clamps to source bounds. More context can retain door edges or handles; too much context can reintroduce other objects. The reasoner sees an RGB rectangular crop, not a segmentation mask. Full-frame versus crop results use different visual evidence and cannot establish which model is better in isolation.'), node('p', 'The saved request includes the parent request/result hashes, source partition, exact frame, detection box and score, and padding. Submission resolves the parent again and rejects changed evidence fields. The actual saved input PNG and crop coordinates are authoritative.'), node('a', 'Browse handoff implementation'));
    guide.lastChild.href = '/resources?section=code';
    panel.append(select, label, button, status, guide); return panel;
}
const renderWithoutHandoff = renderResult;
renderResult = function(record) {
    renderWithoutHandoff(record);
    if (record.status === 'completed' && ['detection','segmentation','tracking'].includes(record.request.options.component)) $('resultBody').prepend(detectionHandoffPanel(record));
    if (record.request.handoff) $('resultBody').prepend(jsonDetails('Detection-to-reasoning provenance', record.request.handoff));
};

// Prompts stay literal when edited; default templates follow target and profile.
let customPrompt = false, promptGeneration = 0;
const promptPanel = node('section'); promptPanel.id = 'promptPanel';
const promptEditor = node('textarea'); promptEditor.id = 'promptEditor'; promptEditor.className = 'prompt-editor'; promptEditor.maxLength = 16000;
promptEditor.setAttribute('aria-label','User prompt sent to the reasoning model');
const promptStatus = node('p'), systemPrompt = node('p'), resetPrompt = node('button','Reset to default prompt');
resetPrompt.id = 'resetPrompt';
promptPanel.append(node('h3','Prompt sent to the model'),systemPrompt,promptEditor,resetPrompt,promptStatus,node('p','Edit the user message above. Image F1 is the exact previewed crop, attached separately. The model chat template is applied at execution and saved with the result. States reuse this message independently for each frame. Keep the door-state JSON fields and F1 reference if you want structured state/rule results; changing the output format can make parsing fail. Custom text stays literal when target or profile changes.','muted'));
$('reasoningOptions').append(promptPanel);
async function refreshPrompt() {
    const generation = ++promptGeneration;
    if (!['reasoning','states'].includes($('component').value)) return;
    try {
        const options = experiment();
        const result = await api('/v1/lab/prompt', options);
        if(generation !== promptGeneration) return;
        if(!customPrompt) promptEditor.value = result.prompt;
        systemPrompt.textContent = 'System message (fixed): ' + (result.system_prompt || '(none)');
        promptStatus.textContent = result.custom ? 'Custom user prompt · saved verbatim with the run. Reset restores the selected target/profile template.' : 'Default template · updates with target and generation profile. Edit to create a custom prompt.';
    } catch(error) { if(generation === promptGeneration) promptStatus.textContent = error.message; }
}
promptEditor.oninput = () => { ++promptGeneration; customPrompt = true; promptStatus.textContent = 'Custom user prompt · saved verbatim with the run.'; };
resetPrompt.onclick = () => { customPrompt = false; refreshPrompt(); };
const experimentWithoutPrompt = experiment;
experiment = function() {
    const options = experimentWithoutPrompt();
    if(customPrompt && ['reasoning','states'].includes(options.component)) options.prompt = promptEditor.value;
    return options;
};
const modelChangedWithoutPrompt = modelChanged;
modelChanged = function() { modelChangedWithoutPrompt(); refreshPrompt(); };
for(const id of ['component','model','target','reasoning']) $(id).addEventListener('change',refreshPrompt);
const loadWithoutPrompt = loadRunSettings;
loadRunSettings = async function(record) {
    customPrompt = record.request.options.prompt != null;
    promptEditor.value = record.request.options.prompt || '';
    await loadWithoutPrompt(record);
    await refreshPrompt();
};
refreshPrompt();

// Named configurations are drafts, not inference results or historical reviews.
const configurationPanel=node('details');configurationPanel.id='configurationPanel';
configurationPanel.append(node('summary','Saved experiment configurations'));
const configurationName=node('input');configurationName.id='configurationName';configurationName.maxLength=100;
const configurationNotes=node('textarea');configurationNotes.id='configurationNotes';configurationNotes.maxLength=4000;configurationNotes.rows=2;
const savedConfiguration=node('select');savedConfiguration.id='savedConfiguration';
const configurationStatus=node('p');configurationStatus.setAttribute('role','status');
for(const [text,control] of [['Configuration name',configurationName],['Notes: purpose and expected comparison',configurationNotes],['Saved configuration',savedConfiguration]]){const label=node('label',text);label.append(control);configurationPanel.append(label)}
const saveConfiguration=node('button','Save current settings');saveConfiguration.id='saveConfiguration';
const loadConfiguration=node('button','Load selected configuration');loadConfiguration.id='loadConfiguration';
const configurationDetails=node('div');
configurationPanel.append(saveConfiguration,loadConfiguration,configurationStatus,configurationDetails,node('p','Save creates a new named snapshot of the current form, including source, range, crop, model parameters and prompt. Load verifies source identity and previews the inputs; it does not run a model. Reasoning templates are frozen as literal prompts so future template changes do not alter saved text. Reset to default prompt opts back into the current template. Notes describe your intent, not a ground-truth label. Saving again creates a separate entry.','muted'));
$('preset').parentElement.after(configurationPanel);
async function refreshConfigurations(selected='') {
    const result=await api('/v1/lab/configurations');
    savedConfiguration.replaceChildren(new Option('Choose saved settings',''),...result.configurations.map(c=>new Option(`${c.name} · ${c.options.component}/${c.options.model} · ${new Date(c.created_unix*1000).toLocaleString()}`,c.configuration_id)));
    savedConfiguration.value=selected;loadConfiguration.disabled=!selected;
}
savedConfiguration.onchange=()=>{loadConfiguration.disabled=!savedConfiguration.value;configurationDetails.replaceChildren()};
saveConfiguration.onclick=async()=>{
    saveConfiguration.disabled=true;
    try {
        const value=await api('/v1/lab/configurations',{name:configurationName.value,notes:configurationNotes.value,options:experiment()});
        await refreshConfigurations(value.configuration_id);
        configurationDetails.replaceChildren(jsonDetails('Saved configuration YAML',value));
        configurationStatus.textContent='Saved '+value.name+' · '+value.configuration_id+'. No model was run.';
    }catch(error){configurationStatus.textContent=error.message}
    finally{saveConfiguration.disabled=false}
};
loadConfiguration.onclick=async()=>{
    loadConfiguration.disabled=true;
    try {
        const value=await api('/v1/lab/configurations/'+savedConfiguration.value);
        await loadRunSettings({run_id:value.configuration_id,request:{options:value.options}});
        configurationName.value=value.name;configurationNotes.value=value.notes;
        configurationDetails.replaceChildren(jsonDetails('Loaded configuration YAML',value));
        configurationStatus.textContent='Loaded '+value.name+'. Inspect the preview, edit if needed, then Run experiment.';
        $('runStatus').textContent=configurationStatus.textContent;
    }catch(error){configurationStatus.textContent=error.message}
    finally{loadConfiguration.disabled=!savedConfiguration.value}
};
refreshConfigurations().catch(error=>configurationStatus.textContent=error.message);
