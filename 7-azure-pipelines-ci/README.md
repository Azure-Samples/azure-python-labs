# Configure continuous integration builds for a Python project hosted in GitHub

Ensuring that your project can be built at all times, and that all your tests
pass, is an important part of maintaining project quality, stability and
velocity.  By introducing a continuous integration build setup, you can
validate that every pull request builds and that the tests pass before it's
even merged.

[Azure Pipelines](https://azure.com/pipelines) provides cloud-hosted build
agents to build your project on Linux, Windows and macOS, for any software
project in any language.  And Azure Pipelines is free for Open Source
projects to build and test their software.

In this lab you will:

- Set up Azure Pipelines to build and test a Python project hosted in GitHub.
- Customize the build by configuring the YAML build definition.
- Validate pull requests using GitHub Checks and Azure Pipelines

## Prerequisites

* If you don't have a GitHub account, create a free account before you begin.
You can [join GitHub](http://github.com/join) to get started.

* If you don't have a Microsoft account, create a free account before you begin.  You can [create a Microsoft account](https://www.microsoft.com/account) to get started.

## 1. Fork the Microsoft cloud scanner project

To demonstrate a continous integraiton build and test setup, we'll use a
small, modern Python application with unit tests.  We'll make a copy of this project, or a "fork", into our own GitHub repository so that we can work on it freely, without impacting the original open source  project.

* Open your browser and navigate to [https://github.com/ethomson/cloud-scanner](https://github.com/ethomson/cloud-scanner).

* Next, sign in to GitHub.

  ![sign in](images/1-signin.png)

* When you've signed in, you'll be returned to the Microsoft Cloud Scanner repository.  Click Fork in the top right corner of the repository page.

  ![fork](images/1-fork.png)

* If you are part of any GitHub organizations, you will be prompted to choose where to fork the repository.  Choose your personal GitHub account, on the top of the list.

  ![select account](images/1-selectaccount.png)

  (If you are not prompted, skip this step.)

* Wait a few seconds while the fork completes.

  ![forking](images/1-forking.png)

Now, you will be at _your own_ copy of this repository, which is a duplicate of the original repository.  You can work in this repository, commit to it and configure a continuous integration build without impacting the original open source project.

## 2. Add the Azure Pipelines app to this repository

Enable Azure Pipelines for thie repository by adding the GitHub app from the GitHub Marketplace.

* Open the GitHub Marketplace by clicking on Marketplace in the banner at the top of the GitHub page.

  ![marketplace](images/2-marketplace.png)

* In the GitHub Marketplace search box, type "Azure Pipelines"

  ![search](images/2-search.png)

* On the search results page, select "Azure Pipelines"

  ![select](images/2-select.png)

* On the Azure Pipelines application page, scroll down to the bottom of the page.  Then select "Install for free".

  ![install for free](images/2-installfree.png)

* On the confirmation page, select "complete order and begin installation".

  ![completeorder](images/2-completeorder.png)

* On the installation page, provide a final validation that you want to install Azure Pipelines.

  ![confirm](images/2-confirm.png)

## 3. Set up an Azure DevOps account

Create a new Azure DevOps account so that you can enable Azure Pipelines for your repository.

* On the new account page, you can give your Azure DevOps organization a custom name or choose the default, which is derived from your GitHub username.

* Set your Project name to "cloud-scanner".

  ![New Account](images/3-newaccount.png)

* Click Continue, and wait a few seconds while your account is created.

* Once your account is created, you'll need to authorize it so that it can be connected to GitHub.

  ![Authorize](images/3-authorize.png)

Now you have an Azure DevOps account created, and Azure Pipelines is linked to GitHub so that you can set up continuous integration builds and pull request validation.

## 4. Set up your Continuous Integration build definition

Azure Pipelines can examine your repository so that it can try to determine what kind of software project you're building.  It can then suggest a build definition to build and test your software project.  For basic projects, these definitions are often adequate, and for more complex projects, they serve as a good starting point.  You'll need to select the repository that you want to build to get started.

* Select the repository that you want to build.  This will be the `cloud-scanner` repository that you forked in step 1.  (It should be at the top of the repository list.)

  ![Select repository](images/4-selectrepo.png)

* Azure Pipelines will now analyze your repository to determine what language is it, and how it should build it.  Once it's finished with the examination, it will present you with some choices.  Select "Python package" from the options.

  ![Python](images/4-python.png)

* Now, Azure Pipelines will show you the build definition.  Build definitions are written in the YAML language and checked in to the repository, right next to the code they build.  This is a technique called "configuration as code" and is helpful since it versions the steps to build the code alongside the code itself.

  You can scroll through the YAML to see how your project will be built.  First, a trigger is set up so that the build will be automatically executed when there's a new push to the master branch, or a pull request is opened against it.

  Next, the pool is set up.  This build will run on the `Ubuntu-16.04` pool, which indicates that it will run on Azure Pipelines' cloud-hosted Linux build agents.

  Then, a matrix is set up.  This allows us to set up multiple builds to run that have minor changes.  In this case, we'll run all the build steps while varying the version of Python being executed.  By default, Azure Pipelines will run your build on Python 2.7, 3.5, 3.6 and 3.7.

  Then the build steps are run:  the version of Python is selected (according to the matrix), the dependencies are installed with `pip` and then `pytest` is run.

*  In this case, the project we're building only supports Python 3.6 and newer.  But Azure Pipelines offers to build Python 2.7, and Python 3.5-3.7.  So the suggested pipeline is not suitable for this project.

   We want to _remove_ Python 2.7 and Python 3.5 from this build pipeline.  In the build YAML, delete lines 13-16.

   ![edit yaml](images/4-edityaml.png)

   These are the lines that specify that Azure Pipelines.  Your matrix should then look like:

   ```
   strategy:
     matrix:
       Python36:
         python.version: '3.6'
       Python37:
         python.version: '3.7'
   ```

* Once you've updated your build YAML, click "Save and Run".  Then on the pop-up dialog, click "Save and Run" again.  This will finalize the configuration, checking in the YAML into your repository and queue your first build.

  ![save and run](images/4-saveandrun.png)

Once you've saved your configuration, Azure Pipelines will set up GitHub so that builds are queued for new pushed into your master branch and new pull requests.  Then Azure Pipelines will start your first build.

## 5. Watch your project build

Now your build will start.  Azure Pipelines will locate two unused Ubuntu 16.04 build agents that are hosted in Azure to perform your build, and start your builds on them.  You're performing two builds in paralell, one for each version of Python that you're building and testing on, as configured by your matrix in step 4.

![parallel jobs](images/5-paralleljobs.png)

You can watch each step as it's being executed, and you can see the build output from each step.  You can click on any step that's being executed, or has completed, to see the detailed line-by-line output.

After about a 45 seconds, both jobs should be complete, and should succeed.  You'll see this indicated by green success check marks next to each job.

![success](images/5-success.png)

You'll also see the overall status for this build, in the title, be decorated with a green check mark as well.

You can now review the build output to understand how this project is build, and you can also click the "Tests" tab to see the output from unit tests.  (They're all passing, as we would hope.)

![tests](images/5-tests.png)

## 6. Create a pull request to your repository

Now that we've set up Azure Pipelines and validated that our builds work correctly and that the tests run, we can see how this is useful for validating pull requests against our project.

Let's add a "badge" for PyPI to the project's README, so that users know that this project is on PyPI.

* Navigate back to your project's repository on GitHub.  You can click on the repository name at the top of the build output page.

  ![go to github](images/6-gotogithub.png)

* On your GitHub repository, scroll down to the README section (below the files list).  Then click the pencil on the right side of the README's header.  This will let you start editing the README.

  ![edit readme](images/6-editreadme.png)

* You'll see the markdown for the README.  On line three, you'll see an existing badge, this is the build badge for the repository, that shows the status of the continuous integration build.

  ![readme](images/6-readme.png)

  (Note that it shows the _original_ project's build status, not your forked repository's build.  This is standard for open source projects.)

  Add a PyPI badge below this, on line 4.  Pasting in the following markdown:

   ```
   [![PyPI](https://img.shields.io/pypi/v/cloud-scanner.svg)](https://pypi.org/project/cloud-scanner/)
   ```

* Scroll down to the bottom of the page to commit this change.  In the first text field, the commit title, enter "Add PyPI Badge".

  Select the radio button that says "Create a **new branch** for this commit and start a pull request."

  ![propose change](images/6-proposechange.png)

  Then click "Propose file change".

* The next page is the new pull request page.  Simply click "Create pull request".

  ![create pull request](images/6-createpr.png)

* Now you'll be taken to the new pull request page.  In the middle of this page is the GitHub Checks section.  Immediately upon creating the pull request, this section is yellow while GitHub ensures that there are no conflicts with the master branch in the pull request that you've opened.  Once that is satisfied, the section will turn green.

  A few seconds later, however, the section should turn yellow again.  At this point, Azure Pipelines will queue a build for the pull request branch, to validate the PR.

  ![build queued](images/6-buildqueued.png)

  Eventually, Azure Pipelines will build the pull request branch, and report the status back, so that you can ensure that you have a successful build and tests on the pull request.

  ![build complete](images/6-builddone.png)

Now you've set up a continuous integration build for your Python project on GitHub, and you've seen how to customize the build and how it operates on GitHub Pull Requests.

## Resources

You can find out more information about Azure Pipelines at [azure.com/pipelines](https://azure.com/pipelines).
