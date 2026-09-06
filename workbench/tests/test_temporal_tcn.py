import numpy as np
import pytest
import torch
from video_workbench.temporal.tcn import CausalMultiStageTCN,ChunkPredictor,AvailableSequenceStream,segmentation_loss

torch.set_num_threads(2)


def test_future_perturbation_and_arbitrary_chunk_equivalence():
    torch.manual_seed(7)
    model=CausalMultiStageTCN(4,3,channels=8,layers=2,stages=2).eval()
    x=torch.randn(2,4,40);valid=torch.ones(2,40,dtype=torch.bool);valid[:,9:12]=False
    with torch.no_grad():
        full=model(x,valid);changed=x.clone();changed[:,:,21:]+=99
        assert torch.allclose(full[...,:21],model(changed,valid)[...,:21],atol=1e-6)
        stream=ChunkPredictor(model);chunks=[];start=0
        for end in (1,7,18,19,33,40):
            chunks.append(stream.push(x[:,:,start:end],valid[:,start:end]));start=end
        assert torch.allclose(full,torch.cat(chunks,dim=-1),atol=1e-6)
        assert stream.history_x.shape[-1]==model.receptive_field-1==12
        altered=x.clone();altered[:,:,9:12]=10000
        assert torch.allclose(full,model(altered,valid),atol=1e-6)


def test_label_mask_padding_and_gradient_exclusion():
    torch.manual_seed(8)
    logits=torch.randn(2,1,3,8,requires_grad=True);target=torch.zeros(1,8,dtype=torch.long)
    mask=torch.tensor([[True,True,False,False,True,False,False,False]])
    changed=target.clone();changed[~mask]=-999
    loss=segmentation_loss(logits,target,mask)
    assert loss==segmentation_loss(logits,changed,mask)
    loss.backward()
    assert (logits.grad[:,:,:,~mask[0]]==0).all()
    empty=segmentation_loss(logits,changed,torch.zeros_like(mask));assert empty.item()==0
    with pytest.raises(ValueError):segmentation_loss(logits,changed,torch.ones_like(mask))


def test_delayed_feature_blocks_future_inputs_and_replays_same_prefix():
    from copy import deepcopy
    from video_workbench.temporal.fixtures import oracle_sequences
    s=oracle_sequences(2)['normal'];s.available_us[1]=int(s.end_us[5])
    torch.manual_seed(2);model=CausalMultiStageTCN(4,3,channels=4,layers=1,stages=1).eval()
    altered=deepcopy(s);altered.features[2:]+=100
    left=AvailableSequenceStream(model,s);right=AvailableSequenceStream(model,altered)
    asof=int(s.end_us[4])
    assert left.advance(asof)==right.advance(asof)
    assert left.index==right.index==1
    outputs=left.advance(int(s.end_us[5]))
    assert [r['index'] for r in outputs]==list(range(1,6))
    assert all(r['available_us']==s.end_us[5] for r in outputs)
    with pytest.raises(ValueError):left.advance(0)
