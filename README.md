# Josh Interview for Reach 7/22/20
For this interview I implemented a simple FastAPI service. I then created a docker image that would run that service. Lastly, I used kubernetes to deploy the service. 

The main challenge I ran into was setting up rate limiting. It seems to be impossible with FastAPI out of the box. I was trying to use Traefik for it, but am hitting some sort of bug getting requests flowing into the entrypoint. 

The docker image I uploaded can be found at 4dahalibut/reach-interview:reach and was uploaded to DockerHub. This image was manually tested directly, and the service and deployment yamlfiles were manually tested, using minikube. 

For the worker, I am just using the builtin FastAPI asynchronous job functionality. This seems to me to be okay because the email notification should happen quickly and smoothly, and retrying can be handled during the proceeding session if the server sees that the email hadn't been sent successfully. 

## Kubernetes Cluster Specification
For this app to be deployed to a real cluster such as through GKE, many pieces of the infrastructure would have to be fleshed out. 
* The app would probably need to be changed from using sqlite to using Postgres or MongoDB, as Sqlite is mostly made for local data storage, instead of implementing a shared repository of enterprise data. Once that is done, a Postgres deployment could live inside of kubernetes, or one could choose to use Google Cloud SQL or it's counterparts on other cloud platforms instead. One would have to explore these options for cost optimization. 
* Currently the app uses Redis for rate limiting which would need to be deployed to the kubernetes cluster, but 
* The rate limiting should be moved into Traefik, so that the app can't be DDOSed. 
* Setting up Traefik is best done through Helm for some sane defaults, but the rate limiting middleware and the ingress route would need to be added to the set of yamlfiles applied to the cluster. 
* Kibana and Grafana should be deployed to the cluster, to read the logs from this service. 
* Enough compute should be configured to run the app and the associated amenities. I don't think there are any requirements for the compute, because this app should be easily scalable horizontally through reconfiguring the deployment, or through using the Horizontal Pod Autoscaler
