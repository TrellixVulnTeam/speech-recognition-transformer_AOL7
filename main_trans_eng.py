from pytorch_lightning.trainer.trainer import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from scipy.sparse import (
    csr_matrix,
)  # TODO(tilo): if not imported before torch on HPC-cluster it throws: ImportError: /lib64/libstdc++.so.6: version `CXXABI_1.3.9' not found

from src.model.transformer.lightning_model_eng import LightningModel
import torch.backends.cudnn as cudnn
import random
import torch as t
import os
import argparse
from warnings import filterwarnings
from pytorch_lightning.logging.test_tube_logger import TestTubeLogger
filterwarnings('ignore')


def get_args():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--nb_gpu_nodes', type=int, default=1)
    parent_parser.add_argument('-seed', default=1, type=int)
    parent_parser.add_argument('-epochs', default=200, type=int)
    parser = LightningModel.add_model_specific_args(parent_parser)
    return parser.parse_args()

def main(hparams):
    model = LightningModel(hparams)
    if hparams.seed is not None:
        random.seed(hparams.seed)
        t.manual_seed(hparams.seed)
        cudnn.deterministic = True
    exp_root = 'exp'
    log_folder = 'lightning_logs'
    log_root = os.path.join(exp_root, log_folder)
    logger = TestTubeLogger(exp_root, name=log_folder, version=1020)
    checkpoint = ModelCheckpoint(filepath='exp/lightning_logs/version_1020/checkpoints/',
                                 monitor='val_mer', verbose=1, save_top_k=-1)
    trainer = Trainer(
        logger=logger,
        early_stop_callback=False,
        checkpoint_callback=checkpoint,
        # checkpoint_callback=checkpoint,
        # fast_dev_run=True,
        # overfit_pct=0.03,
        # profiler=True,
        default_save_path='exp/',
        val_check_interval=1.0,
        log_save_interval=50000,
        row_log_interval=50000,
        gpus=1,
        # precision=16,
        # distributed_backend='ddp',
        nb_gpu_nodes=hparams.nb_gpu_nodes,
        max_nb_epochs=hparams.epochs,
        gradient_clip_val=5.0,
        min_nb_epochs=3000,
        use_amp=True,
        amp_level='O1',
        nb_sanity_val_steps=0
    )
    # if hparams.evaluate:
    #     trainer.run_evaluation()
    # else:
    trainer.fit(model)

if __name__ == '__main__':
    main(get_args())