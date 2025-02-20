import torch
from torch import nn
from torch.utils.data import DataLoader
import torchmetrics

def train_one_epoch(
  model:nn.Module,
  criterion:callable,
  optimizer:torch.optim.Optimizer,
  data_loader:DataLoader,
  metric:torchmetrics.Metric,
  device:str,
  save_ratio:int
) -> None:
  '''train one epoch
  
  Args:
      model: model
      criterion: loss
      optimizer: optimizer
      data_loader: data loader
      device: device
  '''
  model.train()
  total_loss = 0
  count = 0
  for X, y in data_loader:
    X, y = X.to(device), y.to(device)
    output = model(X)
    loss = criterion(output, y)
    total_loss += loss.item()
    count += 1
    if count == save_ratio:
      yield total_loss
      total_loss = 0
      count = 0
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    metric.update(output, y)


def main(cfg):
  import numpy as np
  import pandas as pd
  from torch.utils.data.dataset import TensorDataset
  from nn import ANN
  from tqdm.auto import trange

  train_params = cfg.get('train_params')
  device = torch.device(train_params.get('device'))
  
  files = cfg.get('files')
  X_trn = torch.tensor(pd.read_csv(files.get('X_csv'), index_col=0).to_numpy(dtype=np.float32))
  y_trn = torch.tensor(pd.read_csv(files.get('y_csv'), index_col=0).to_numpy(dtype=np.float32))

  dl_params = train_params.get('data_loader_params')
  ds = TensorDataset(X_trn, y_trn)
  dl = DataLoader(ds, **dl_params)

  Model = cfg.get('model')
  model_params = cfg.get('model_params')
  model_params['input_dim'] = X_trn.shape[-1]
  model = Model(**model_params).to(device)

  Optim = train_params.get('optim')
  optim_params = train_params.get('optim_params')
  optimizer = Optim(model.parameters(), **optim_params)

  loss = train_params.get('loss')
  metric = train_params.get('metric').to(device)
  values = []
  pbar = trange(train_params.get('epochs'))
  for _ in pbar:
    for train_loss in train_one_epoch(model, loss, optimizer, dl, metric, device, save_ratio=50):
      if wandb_params.get('use_wandb'):
        wandb.log({"Training loss": train_loss / 50})
      print(f'Train loss: {train_loss / 50:.3f}')
        
    values.append(metric.compute().item())
    metric.reset()
    pbar.set_postfix(trn_loss=values[-1])
  torch.save(model.state_dict(), files.get('output'))
def get_args_parser(add_help=True):
  import argparse
  
  parser = argparse.ArgumentParser(description="Pytorch K-fold Cross Validation", add_help=add_help)
  parser.add_argument("-c", "--config", default="./config.py", type=str, help="configuration file")

  return parser

if __name__ == "__main__":
  import wandb
  args = get_args_parser().parse_args()
  exec(open(args.config).read())
  config = config
  wandb_params = config.get("wandb")
  if wandb_params.get('use_wandb'):
    wandb.init(project='Jeju_traffic_prediction_TRAIN')
    # 실행 이름 설정
    wandb.run.name = wandb_params.get('wandb_runname')
    wandb.run.save()
    wandb.config.update(config)
  main(config)
