# Advanced Algorithms and Graph Mining Exam

![Italy-COVID19](https://github.com/pisalore/AAGM_exam/blob/master/images/italy.jpg)

In this repo it is collected my project for the AAGM exam, Master Degree at
University of Studies of Florence, Italy.

Two different works are provided. Both use the COVID-19 data made available from Italian Department of Civil Protection
in their [GitHub Repo](https://github.com/pcm-dpc/COVID-19)

#### 1. First Part: Building the graph of provinces and running some algorithms

The first part of the project, Floyd-Warshall _ClusteringCoeff.py, contains the implementations of two different 
algorithm for Graph construction with [NetworkX Module](https://networkx.github.io/) 
* One which simply iterate over all the nodes twice in order to assign an edge if a closeness criteria is satisfied (O(n^2))
* The other does it better, using sorting and binary search( O(nlogn))
    
and two algorithms which are runned on the mentioned Graphs, of different dimension and sparseness (depending on closeness
criteria mentioned above)
* [Floyd-Warshall Algorithm](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
* [Clustering Coefficient]( https://it.wikipedia.org/wiki/Coefficiente_di_clustering )

#### 2. Second Part: Pandas

The second part of the project concerns the use of Pandas, Matplotlib and other tools for data analysis and visualization
enjoying Python calculation power. Obviously this data analysis has been made about COVID-19 pandemic in Italy.
At this link it's possible to visualize the Jupyter Notebook, powered by nbviewer: 
[COVID-19 In Italy](https://nbviewer.jupyter.org/github/pisalore/AAGM_exam/blob/master/pandas_exam.ipynb)
