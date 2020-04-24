import commands
services=4
for i in range(1, services+1):
    commands.getstatusoutput("oc process -f deploy.yaml -p SERVICES={} -p IDENTITY={} | oc create -f -".format(services, i))
    commands.getstatusoutput("oc expose deployment/mesh-demo-{}".format(i, i))