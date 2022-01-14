# Knowledge Graph Construction 
This is a software implementation for the project 'Knowledge Graph Construction'. The project’s goal is to build a Knowledge Graph (KG) about food products sold on Amazon. For the construction, the Resource Description Framework (RDF) was used 


## The program's installation
The program can be executed by cloning this git-repository and running the **builddKG.py** program. This program can be executed in the Windows command shell (cmd) or in a development environment (IDE) that supports a Python Interpreter like PyCharm or Visual Studio Code.


>**Notes: This project's implementation uses the latest version of Python (Python 3.10) so make sure you use this or a compatible version. Moreover, the program was only tested on the operation system Windows. So the program’s execution could lead to problems on Linux or Mac OS because of the naming conventions of the paths. In addition, you have to ensure, you installed all imported libraries in the programs as well as the Chrome Web-Driver on your system.**


## The program's usage 
After running the program **buildKG.py** on the command shell, the program asks you to enter an URL of a food product that is sold on Amazon. This entry causes the execution of the program getFoodProduct.py, it extracts the HTML code of the webpage and scraps all the necessary product information. After the data extraction, the program ‘BuildKG.py’ creates the knowledge graph and exports it to a Turtle file (foodGraph.ttl). This whole procedure is repeated  until the user enters an empty URL. In this case, the Data Cleaning program (CleanData.py) will be executed. This program works with the user in the way it uses the user’s input to modify and remove data from the knowledge graph.
