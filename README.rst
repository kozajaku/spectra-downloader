Spectra analyzer
================

Task
----

The aim of this work is to create a tool for analyzing a dimensionality reduction of a chosen astronomical spectrum.

The tool has a web interface written using Python framework Flask. Astronomical spectra can be downloaded from the Virtual Observatory archive using specialized astronomical protocols SSAP and Datalink. The principle of these protocols is to query a specific URL address using HTTP protocol in order to obtain spectrum itself or XML formatted file containing information about a construction of additional URL addresses. The tool uses the Python library `requests` for fetching a content from the specified URL address and the library `xml.sax` to parse XML documents. For downloading either multiple threads or the Python `asyncio` library should be used. 

Any spectrum either downloaded by the tool or already present in the filesystem can be chosen for further inspection. The tool visualize the selected spectrum and it also allows user to change parameters of dimensionality reduction method continual wavelet transformation. The transformed spectrum is also visualized and a user can observe changes between the original and the transformed spectrum. The task of this tool is to allow a user to find out a transformation parameters threshold where the spectrum still has the most of an original important information but its size is reducted by the dimensionality reduction method. The tool uses Python modules `matplotlib`, `numpy` and `mply` for the spectrum manipulation and transformation.

