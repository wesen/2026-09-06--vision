// Compare saved evidence at exact source timestamps; never fill missing samples.
function comparisonInspector(records) {
    const panel=node('section');panel.id='comparisonInspector';
    panel.append(node('h3','Compare exact evidence in time'));
    const sameSource=records[0].request.evidence.source.video_sha256===records[1].request.evidence.source.video_sha256;
    if(!sameSource){panel.append(node('p','These runs use different video bytes. A shared source clock would be misleading; inspect each recording separately.'));return panel}
    const timestamps=[...new Set(records.flatMap(r=>r.request.evidence.frames.map(f=>f.pts_us)))].sort((a,b)=>a-b);
    if(!timestamps.length){panel.append(node('p','No saved input frames to compare.'));return panel}
    panel.append(node('p','Both runs reference the same source video. Select an exact sampled timestamp to inspect A and B. A missing sample stays missing. The video below plays source context; the saved images and answers update only when you select a sampled timestamp.','muted'));
    const player=node('video');player.id='comparisonVideo';player.controls=true;player.preload='metadata';player.style.maxHeight='320px';player.src='/v1/lab/sources/'+encodeURIComponent(records[0].request.options.episode_id)+'/video';
    panel.append(player);
    const clock=node('p','Source playback time —','muted');player.ontimeupdate=()=>clock.textContent=`Source playback time ${player.currentTime.toFixed(3)} s · playback does not generate or interpolate outputs.`;panel.append(clock);
    const controls=node('div',undefined,'row');
    const previous=node('button','Previous sample'),next=node('button','Next sample'),select=node('select');select.id='comparisonTimestamp';select.setAttribute('aria-label','Exact comparison timestamp');
    timestamps.forEach(t=>select.append(new Option(`${(t/1e6).toFixed(6)} s`,String(t))));controls.append(previous,select,next);panel.append(controls);
    const aligned=node('div',undefined,'result-grid');aligned.id='comparisonAligned';panel.append(aligned);
    const table=node('table');table.id='comparisonSampleTable';const header=node('tr');['Exact source time','A saved output','B saved output'].forEach(x=>header.append(node('th',x)));table.append(header);
    function pointSummary(run,t){const f=run.request.evidence.frames.find(f=>f.pts_us===t);if(!f)return 'No sampled input';const row=run.result?.records?.find(r=>r.frame.id===f.id);if(row?.state)return `${row.state.toUpperCase()} · ${row.parsed.status}`;if(row?.detections)return `${row.detections.length} detections`;return 'Saved input; inspect containing windows'}
    for(const t of timestamps){const row=node('tr');const cell=node('td'),button=node('button',`${t/1e6} s`);button.onclick=()=>{select.value=String(t);show(true)};cell.append(button);row.append(cell,...records.map(r=>node('td',pointSummary(r,t))));table.append(row)}
    const overview=node('details');overview.append(node('summary','Aligned sample overview'),table);panel.append(overview);
    function show(save) {
        const t=Number(select.value);previous.disabled=select.selectedIndex===0;next.disabled=select.selectedIndex===timestamps.length-1;
        const seek=()=>{player.currentTime=t/1e6};if(player.readyState>=1)seek();else player.onloadedmetadata=seek;
        aligned.replaceChildren();
        records.forEach((run,i)=>{
            const col=node('article');col.append(node('h3',`${i?'B':'A'} · ${run.request.options.model} · ${run.status}`),node('p',run.run_id,'muted'));
            const frame=run.request.evidence.frames.find(f=>f.pts_us===t);
            if(frame){
                const row=run.result?.records?.find(r=>r.frame.id===frame.id);
                const img=node('img');img.style.maxHeight='280px';img.style.objectFit='contain';img.src=artifactUrl(run.run_id,row?.overlay||frame.file);img.alt=`${i?'B':'A'} exact evidence at ${t/1e6} seconds`;col.append(img,node('p',`Exact PTS ${t/1e6} s · ${frame.width}×${frame.height} · source crop ${frame.crop_xyxy.join(', ')}`));
                if(row?.state)col.append(node('h3',row.state.toUpperCase()),node('p','Validation: '+row.parsed.status),node('p',row.parsed.answer?.rationale||row.parsed.reason||'No validated explanation'));
                if(row?.detections)col.append(node('p',row.detections.map(d=>`${d.class_name} ${d.score.toFixed(3)}`).join(' · ')||'No detections'));
                const runtime=row?.runtime;
                const prompt=runtime?.prompt||run.request.prompt_snapshot?.prompt;
                if(prompt){const details=node('details');details.append(node('summary','Actual user prompt'),node('pre',prompt));col.append(details)}
                if(runtime){col.append(jsonDetails('Prompt, raw output and runtime YAML',runtime));const raw=node('details');raw.append(node('summary','Raw model response'),node('pre',runtime.raw));col.append(raw)}
                col.append(jsonDetails('Exact frame identity YAML',frame));
            }else col.append(node('p','No sampled input at this exact timestamp. No neighboring answer is substituted.','muted'));
            const windows=run.result?.action_windows||run.result?.windows||[];
            const containing=windows.filter(w=>w.start_us<=t&&t<w.end_us);
            if(containing.length){col.append(node('h4','Windows containing this time'));for(const w of containing)col.append(node('p',`${w.start_us/1e6}–${w.end_us/1e6} s · ${w.prediction||'cosine '+w.score.toFixed(4)}`));col.append(node('p','These predictions describe intervals, not exact point-state observations.','muted'))}
            aligned.append(col);
        });
        if(save){const url=new URL(location.href);url.searchParams.set('compare_time_us',String(t));history.replaceState(null,'',url);$('comparisonLink').href=url.href}
    }
    select.onchange=()=>show(true);previous.onclick=()=>{select.selectedIndex--;show(true)};next.onclick=()=>{select.selectedIndex++;show(true)};
    const linked=new URLSearchParams(location.search).get('compare_time_us');
    if(linked!==null&&timestamps.includes(Number(linked)))select.value=String(Number(linked));
    else if(linked!==null)panel.append(node('p','The linked timestamp is not sampled by these runs; showing the first available timestamp.','muted'));
    show(false);return panel;
}
