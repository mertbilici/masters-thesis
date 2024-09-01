from ape import accounts, project, networks

def main():
    deployer = accounts.test_accounts[0]
    registration = deployer.deploy(project.Registration)
    deployer.deploy(project.HashList, registration.address)