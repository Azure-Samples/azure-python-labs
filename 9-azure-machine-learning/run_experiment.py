from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.compute_target import ComputeTargetException
from azureml.core import Experiment, Environment, ScriptRunConfig, Workspace
from azureml.core.conda_dependencies import CondaDependencies

def submit():
    # define workspace
    ws = Workspace.from_config()

    # create compute if it does not already exist
    cluster_name = "goazurego"

    try:
        target = ComputeTarget(workspace=ws, name=cluster_name)
        print(f"Found existing cluster - {cluster_name}.")
        
    except ComputeTargetException:
        # create a configuration
        compute_config = AmlCompute.provisioning_configuration(vm_size="STANDARD_D2_V2", max_nodes=2, min_nodes=0)

        target = ComputeTarget.create(ws, cluster_name, compute_config)

    target.wait_for_completion(show_output=True)

    # use the curated tensorflow 1.15 environment
    environment_name = "AzureML-TensorFlow-1.15-Inference-CPU"
    tf_env = Environment.get(workspace=ws, name=environment_name)

    # create script run configuration
    src = ScriptRunConfig(source_directory=".", script="train.py",
        compute_target=target, environment=tf_env)

    src.run_config.target = target

    # create an experiment
    experiment_name = "pycon-experiment"
    experiment = Experiment(workspace=ws, name=experiment_name)
    
    # run experiment
    run = experiment.submit(config=src)
    run.wait_for_completion(show_output=True)

    return True

if __name__ == "__main__":
    submit()
