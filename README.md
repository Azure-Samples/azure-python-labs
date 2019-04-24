# Build a Movie Recommendation System with Azure Machine Learning 
This tutorial will walk through how to build a Movie Recommender system trained with a Simple Algorithm for Recommenders (SAR) for the [Movielens dataset](https://grouplens.org/datasets/movielens/) on [Azure Machine Learning service](https://docs.microsoft.com/azure/machine-learning/service/overview-what-is-azure-ml). It demonstrates how to use the power of the cloud to manage data, switch to powerful GPU machines, and monitor runs while training a model. You will also be able to 

You will: 
- Connect to an Azure Machine Learning service workspace
- Pull movielens data from a datastore
- Connect to cpu and gpu machines from [Azure Machine Learning Compute](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-set-up-training-targets#amlcompute)
- Create a training script using the recommender repo's [util functions](https://github.com/Microsoft/Recommenders/tree/master/reco_utils) for SAR and add logging information
- Submit the training job to AzureML, and monitor the run with a jupyter widget
- Test an existing model with new user data
**Optional part 2:** 
- Deploy the model to a web service using Azure Container Instance. 
(short, 1-3 sentenced, description of the project)



## Getting Started
- Clone in Azure Notebooks
