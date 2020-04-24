import commands
services=5
for i in range(0, services):
    commands.getstatusoutput("oc process -f deploy.yaml -p SERVICES={} -p IDENTITY={} | oc create -f -".format(services, i))
    commands.getstatusoutput("oc expose deployment/mesh-demo-{}".format(i, i))