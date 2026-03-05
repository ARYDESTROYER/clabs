# Step 1: Use  Node.js alpine image
FROM node:22-alpine

# Step 2: Set the working directory inside the container
WORKDIR /home/labDirectory

# Step 3: Create home directory and all the folders inside it
RUN mkdir /home/.evaluationScripts

# Step 4: Expose the port on which the React app will run
EXPOSE 30000

# Step 5: Add necessary binaries
RUN apk update && apk add bash && apk add python3~3.12

# Step 5: Start the React app
CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/.bodhiFiles/init.sh; while :; do sleep 10; done" ]
