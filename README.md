# Josh Interview for Reach 7/22/20
For this interview I implemented a simple FastAPI service. I then created a docker image that would run that service. Lastly, I used kubernetes to spin serve the service in a scalable manner. 

The main challenge I ran into was setting up rate limiting. It seems to be impossible with FastAPI out of the box. I was trying to use Traefik for it, but am hitting some sort of bug getting requests flowing through it. However, I think the IngressRoute I have uploaded is correct, and there was something wrong with my local setup for why it didn't work. Otherwise, I would have included a test testing the rate limiting. 

For this app to be deployed, there would also have to be a sqlite deployment as well as monitoring and metrics. All secrets are also currently hardcoded, so these would have to become environment variables passed in by k8s. Also, a cloud k8s provider would have to be chosen to provide nodes to run on. I don't think there are any specific requirements on CPU, but for memory, I think that 8 gigabytes would be more than sufficient. 

The docker image I uploaded can be found at 4dahalibut/reach-interview:reach and was uploaded to DockerHub. This image was manually tested directly, and the service and deployment yamlfiles were manually tested, using minikube. 

For the worker, I am just using the builtin FastAPI asynchronous job functionality. This seems to me to be okay because the email notification should happen quickly and smoothly, and retrying can be handled during the proceeding session if the server sees that the email hadn't been sent successfully. 
