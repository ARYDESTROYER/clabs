# Instructions  
  
## General:  
1. #### To create Docker image using the Dockerfile -  
    ```docker buildx build -t {react/unix/html/css/js}-lab:latest .```  
2. #### To run each Lab locally go inside that lab's folder and run -  
    a. ``docker run -it --rm -p 30000:30000 -v .:/home/.evaluationScripts react-lab``  
    b. ``docker run -it --rm -v .:/home/.evaluationScripts {unix/html/css}-lab``  
    c. ``docker run -it --rm -p 30000:30000 -v ./.evaluationScripts:/home/.evaluationScripts -v ./labDirectory:/home/labDirectory js-lab``  

## Upload:
1. #### To generate the upload .tgz binaries of a lab use ``./prepup.sh <lab_name>``
2. #### In Add Script section add *Name - Evaluate* and *Script - /home/.evaluationScripts/evaluate.sh*  
