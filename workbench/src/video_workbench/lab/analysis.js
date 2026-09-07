// Comparisons and reviews always bind saved run IDs, never current form values.
let historyRuns=[];
const oldRefreshHistory=refreshHistory;
refreshHistory=async function(){await oldRefreshHistory();try{historyRuns=(await api('/v1/lab/runs')).runs;for(const id of ['compareA','compareB']){const previous=$(id).value;$(id).replaceChildren(...historyRuns.map(r=>new Option(`${r.request.options.component} / ${r.request.options.model} · ${r.run_id}`,r.run_id)));if(historyRuns.some(r=>r.run_id===previous))$(id).value=previous}if($('compareA').value===$('compareB').value&&historyRuns.length>1)$('compareB').selectedIndex=1}catch(e){fail(e)}};
function addPlot(container,windows){const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 850 220');svg.setAttribute('role','img');svg.setAttribute('aria-label','Cosine similarity over source time');svg.style.width='100%';const scores=windows.map(w=>w.score),lo=Math.min(...scores)-.02,hi=Math.max(...scores)+.02,t0=windows[0].start_us,t1=Math.max(...windows.map(w=>w.end_us));const x=t=>60+(t-t0)/Math.max(1,t1-t0)*750,y=s=>175-(s-lo)/(hi-lo)*145;for(let i=0;i<4;i++){const value=lo+(hi-lo)*i/3;const text=document.createElementNS(ns,'text');text.setAttribute('x','4');text.setAttribute('y',y(value)+5);text.setAttribute('fill','#a4b6b4');text.textContent=value.toFixed(3);svg.append(text)}const line=document.createElementNS(ns,'polyline');line.setAttribute('points',windows.map(w=>`${x(w.start_us)},${y(w.score)}`).join(' '));line.setAttribute('fill','none');line.setAttribute('stroke','#a5ebc8');line.setAttribute('stroke-width','3');svg.append(line);for(const w of windows){const dot=document.createElementNS(ns,'circle');dot.setAttribute('cx',x(w.start_us));dot.setAttribute('cy',y(w.score));dot.setAttribute('r','5');dot.setAttribute('fill','#a5ebc8');const title=document.createElementNS(ns,'title');title.textContent=`${w.start_us/1e6}–${w.end_us/1e6} s: ${w.score.toFixed(4)}`;dot.append(title);svg.append(dot)}for(const t of [t0,t1]){const label=document.createElementNS(ns,'text');label.setAttribute('x',x(t)-15);label.setAttribute('y','207');label.setAttribute('fill','#a4b6b4');label.textContent=(t/1e6).toFixed(1)+' s';svg.append(label)}container.append(svg,node('p','Vertical scale follows this run’s score range. Points mark window starts; hover for exact values. Similarity is not probability.','muted'))}
const oldRenderResult=renderResult;
renderResult=function(record){oldRenderResult(record);const body=$('resultBody');if(record.result?.windows)addPlot(body,record.result.windows);if(record.result?.action_windows){body.append(node('h3','Fresh action predictions'),node('p',record.result.scope));const table=node('table');for(const row of record.result.action_windows){const tr=node('tr');[`${row.start_us/1e6}–${row.end_us/1e6} s`,row.prediction,'PTS '+row.pts_us.map(t=>t/1e6).join(', ')].forEach(x=>tr.append(node('td',x)));table.append(tr)}body.append(table)}if(record.status==='completed'){const panel=node('div');panel.append(node('h3','Review this saved experiment'));const verdict=node('select');['correct','incorrect','unjudgeable'].forEach(v=>verdict.append(new Option(v,v)));verdict.value='unjudgeable';const note=node('textarea');note.placeholder='Describe the visual evidence and what was right, wrong, or impossible to judge.';note.setAttribute('aria-label','Review explanation');const save=node('button','Save independent review'),status=node('p');save.onclick=async()=>{try{const result=await api('/v1/lab/runs/'+record.run_id+'/reviews',{verdict:verdict.value,note:note.value});status.textContent='Saved '+result.review_id+' · source partition '+result.source.split}catch(e){status.textContent=e.message}};const exp=node('a','Export experiment and reviews');exp.href='/v1/lab/runs/'+record.run_id+'/export';exp.target='_blank';panel.append(verdict,note,save,status,exp,node('p','Reviews are separate annotations. Predictions stay unchanged; exported cases retain their source partition.','muted'));body.append(panel);if(['reasoning','states'].includes(record.result?.kind)){const box=node('details');box.open=true;box.append(node('summary','Evaluate a rule using these exact state samples'));const t=node('input');t.type='number';t.step='.1';t.value=record.request.options.start_us/1e6;const label=node('label','User-selected trigger time (source seconds)');label.append(t);const expected=node('select');expected.append(new Option('Door must be closed','false'),new Option('Door must be open','true'));const run=node('button','Evaluate exact-point rule'),out=node('div');run.onclick=async()=>{try{const r=await api('/v1/lab/runs/'+record.run_id+'/rule',{event_us:Math.round(Number(t.value)*1e6),expected_open:expected.value==='true'});out.replaceChildren(node('h3',r.decision.status),node('p',r.decision.reason),node('p',r.scope),jsonDetails('Rule and supporting evidence',r))}catch(e){out.textContent=e.message}};box.append(node('p','This is a manually selected point, not a detected departure. A known matching state gives PASS, a contradiction gives VIOLATION, and no exact sample gives UNKNOWN. Nearby samples are not substituted.'),label,expected,run,out);body.append(box)}}};
$('compareButton').onclick=async()=>{try{const a=$('compareA').value,b=$('compareB').value;if(!a||!b)throw Error('Choose two saved runs');const report=await api('/v1/lab/compare?a='+a+'&b='+b),records=await Promise.all([api('/v1/lab/runs/'+a),api('/v1/lab/runs/'+b)]),body=$('comparison');body.replaceChildren(node('h3',report.same_evidence?'Matched visual evidence':'Different visual evidence'),node('p',report.interpretation));if(report.feature_note)body.append(node('p',report.feature_note));const table=node('table');for(const d of report.differences){const tr=node('tr');[d.field,JSON.stringify(d.a),JSON.stringify(d.b)].forEach(x=>tr.append(node('td',x)));table.append(tr)}body.append(table);const grid=node('div',undefined,'result-grid');for(const r of records){const col=node('article');col.append(node('h3',r.request.options.model+' · '+r.status));for(const row of r.result?.records||[]){const img=node('img');img.src=artifactUrl(r.run_id,row.overlay||row.frame.file);img.alt='Comparison evidence';col.append(img,node('p',`${row.frame.pts_us/1e6} s · ${row.state||row.detections.length+' detections'}`));if(row.parsed)col.append(node('p',row.parsed.answer?.rationale||row.parsed.reason||''))}if(r.result?.action_windows){for(const w of r.result.action_windows)col.append(node('p',`${w.start_us/1e6}–${w.end_us/1e6} s · ${w.prediction}`))}if(r.result?.windows){addPlot(col,r.result.windows);for(const i of r.result.ranking){const w=r.result.windows[i];col.append(node('p',`${w.start_us/1e6}–${w.end_us/1e6} s · ${w.score.toFixed(4)}`))}}grid.append(col)}body.append(grid,jsonDetails('Comparison contract',report))}catch(e){fail(e)}};
$('inspectActions').onclick=async()=>{try{const r=await api('/v1/lab/actions/inspect',selection()),out=$('actionResults');out.replaceChildren(node('p',r.scope||r.reason));if(r.records.length){const table=node('table'),head=node('tr');['Saved model','Window (s)','Prediction','Actual PTS'].forEach(x=>head.append(node('th',x)));table.append(head);for(const row of r.records){const tr=node('tr');[row.model,`${row.start_us/1e6}–${row.end_us/1e6}`,row.prediction,row.pts_us.map(x=>x/1e6).join(', ')].forEach(x=>tr.append(node('td',x)));table.append(tr)}out.append(table)}out.append(jsonDetails('Frozen action provenance',r))}catch(e){fail(e)}};
$('preset').onchange=()=>{const value=$('preset').value;if(!value)return;const presets={masks:{component:'segmentation',model:'yolo11n-seg',fps:2},point:{component:'reasoning',model:'qwen',fps:1},states:{component:'states',model:'qwen',fps:1},native:{component:'embeddings',model:'native_video',fps:2}};const p=presets[value];$('component').value=p.component;componentChanged();$('model').value=p.model;$('fps').value=p.fps;if(value==='point')$('end').value=(Number($('start').value)+.1).toFixed(3);modelChanged();$('previewStatus').textContent='Preset applied. Preview the changed selection before running.'};
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
