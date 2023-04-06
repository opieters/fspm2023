# Leveraging FSPMs for Unconventional Computing with Plants

The repo contains the code, data and slides for the abtsract presented at FSPM2023 by Olivier Pieters.

## Install Instructions

### Presentation

A recent LaTeX distribution is required to compile the presentation. It was tested on TeXLive 2022.

### Simulation Results

https://www.anaconda.com/blog/moving-conda-environments

#### Wheat-FSPM

These simulations are based on the [Wheat-FSPM](https://github.com/openalea-incubator/WheatFspm) from INRAe. 

To install the model, you can use the following commands. It is assumed that you installed [Anaconda](https://www.anaconda.com/distribution/) and [Git](https://git-scm.com/downloads) on your computer.

```bash

conda create -n WheatFspm python=3.7 openalea.mtg openalea.plantgl openalea.lpy alinea.caribu alinea.astk coverage nose sphinx statsmodels -c conda-forge -c fredboudon

conda activate WheatFspm

# based on https://github.com/openalea-incubator/WheatFspm/issues/6

# Clone and install adel
git clone -b python3 https://github.com/rbarillot/adel.git

# Clone and install CN-Wheat
git clone -b develop_MG https://github.com/mngauthier/cn-wheat.git

# Clone and install Elong-Wheat
git clone -b develop_MG https://github.com/mngauthier/elong-wheat.git

# Clone and install Farquhar-Wheat
git clone -b develop_MG https://github.com/mngauthier/farquhar-wheat.git

# Clone and install Fspm-Wheat
git clone -b develop_MG https://github.com/mngauthier/fspm-wheat.git

# Clone and install Growth-Wheat
git clone -b develop_MG https://github.com/mngauthier/growth-wheat.git

# Clone and install Respi-Wheat
git clone -b develop_MG https://github.com/mngauthier/respi-wheat.git

# Clone and install Senesc-Wheat
git clone -b develop_MG https://github.com/mngauthier/senesc-wheat.git
```

It is important that you *do not* clone the global repo of [Wheat-FSPM](https://github.com/openalea-incubator/WheatFspm) because it is not up-to-date. Moreover, each of the linked subrepositories do not work. We also published a snapshot of the working version of the model on [Zenodo](https://doi.org/10.5281/zenodo.7701995).


#### HydroShoot

TODO.
 
We also published a snapshot of the working version of the model on [Zenodo](https://doi.org/10.5281/zenodo.7701995).

#### Data Processing



# Licence

MIT.