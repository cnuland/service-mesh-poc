import commands
import os
services = int(os.getenv("SERVICES", default="4")) # Amount of services to deploy
for i in range(1, services+1): # Create the specified amount of services
    # Use template to set the amount of services and individual identities of the app demo
    print(commands.getstatusoutput("oc process -f app-deploy.yaml -p SERVICES={} -p IDENTITY={} | oc create -f -".format(services, i))[1])
    # Create a service for the newly created deployment
    print(commands.getstatusoutput("oc expose deployment/mesh-demo-{}".format(i, i))[1])