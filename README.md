# Josh Interview for Reach 7/22/20
For this interview I implemented a simple FastAPI service. I then created a docker image that would run that service. Lastly, I used kubernetes to deploy the service. 

The main challenge I ran into was setting up rate limiting. It seems to be impossible with FastAPI out of the box. I was trying to use Traefik for it, but am hitting some sort of bug getting requests flowing into the entrypoint. 

The docker image I uploaded can be found at 4dahalibut/reach-interview:reach and was uploaded to DockerHub. This image was manually tested directly, and the service and deployment yamlfiles were manually tested, using minikube. 

For the worker, I am just using the builtin FastAPI asynchronous job functionality. This seems to me to be okay because the email notification should happen quickly and smoothly, and retrying can be handled during the proceeding session if the server sees that the email hadn't been sent successfully. 

## Kubernetes Cluster Specification
For this app to be deployed to a real kubernetes cluster such as through GKE, many pieces of the infrastructure would have to be fleshed out. 
* The app would need to be changed from using sqlite to using Postgres or MongoDB, as Sqlite is mostly made for local data storage, instead of implementing a shared repository of enterprise data. Once that is done, a Postgres deployment could live inside of kubernetes, or one could choose to use Google Cloud SQL or it's counterparts on other cloud platforms instead. One would have to explore these options for cost optimization. 
* Currently the app uses Redis for rate limiting which would need to be deployed to the kubernetes cluster, but 
* The rate limiting should be moved into Traefik, so that the app can't be DDOSed. 
* Setting up Traefik is best done through Helm for some sane defaults, but the rate limiting middleware and the ingress route would need to be added to the set of yamlfiles applied to the cluster. 
* Kibana and Grafana should be deployed to the cluster, to read the logs and get metrics and alerts from this service. I think that the kibana paid edition is mandatory because alerts are only in this edition. 
* Enough compute should be configured to run the app and the associated amenities. I don't think there are any specific requirements for the compute, because this app should be easily scalable horizontally through reconfiguring the deployment, or through using the Horizontal Pod Autoscaler

## Running the app locally
The app works best in its own Python 3.8.1 virtualenv, with all requirements installed from the 
requirements.txt file. 

You can start the app locally by running "PYTHONPATH . python app/main.py"
However, note that you will have to run some SMTP server for the email functionality to 
work correctly. This can be done for example with this command
```sudo python -m smtpd -n localhost:8025```

You can also start the app by running the docker image locally, or through deploying the 
applying service.yaml and deployment.yaml in the k8s directory. 

I also had to edit the asgi-ratelimit library for some reason, manually applying this bugfix - https://github.com/abersheeran/asgi-ratelimit/commit/779644218d685256dc02d78a1091ffacd63986a1
