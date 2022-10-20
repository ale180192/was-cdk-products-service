# General
Este proyecto implementa un simple catalogo de productos

## Operaciones soportadas
### Productos
Solo los usuarios autenticados pueden crear y actualizar los productos, para listar los productos no es necesario credencial alguna.
* Crear un producto -> Necesita autorizacion
* Actualzar un producto -> Necesita autorizacion
* Listar todos los productos

### Usuarios
* Signup
* Login

## Estructura del proyecto
Este proyecto utilza un enfoque de microservicios(serverless), para el despliegue de la infraestructura se toma el enfoque de infraeestructura como codigo utiliando AWS CDK, En la misma infraestructura vive un pipeline que esta conectado al repositorio de github, cuando se hace un merge hacia la rama master este pipeline se ejectuta. Toda la definicion de la infraestructura esta alojada en la carpeta `infraestructura`.

La API REST con todos los endpoints vive en la carpeta `src`, Utilizamos `Fast API` como framework de desarrollo junto con `Mangum` para poder lograr que la lamda tenga un unico handler y este MANGUN handler se encarga de hacer todo el enrutamiento necesario. La API REST se estructuro con un enfoque de arquitectura hexagonal(DDD o arquitectura limpia), esto con el objetivo de tener desacomplados nuestro dominio de la db, framework web etc.

# AWS CDK
La cuenta root de aws tiene 3 cuentas con el objetivo de separar ambientes, costos y accessos.
* Cuenta pipeline -> aqui se aloja el pipeline, este pipeline tiene permisos para hacer de despliegue en la cuenta de sandbox y la cuenta de produccion
* Cuenta sandbox -> Como primer paso el pipeline realiza el despliegue en esta cuenta
* Cuenta de produccion -> Despues de que el pipeline desplego exitosamente en el sandbox, existe un paso donde se tiene que realizar la aprovacion manual, despues de esto el pipeline continua haciendo el despliegue a esta cuenta de produccion.

## Accounts
![Aws Accounts](images/aws_accounts.png)
## Pipeline
El pipeline es automutable por si mismo.
![Aws Accounts](images/pipeline.png)



## Deploy pipeline
El pipeline se tiene que desplegar de forma manual por una primera y unica vez, para esto tenemos que hacer el boostrapping del proyecto(darle los permisos necesarios). 

```bash
# Cuenta donde se despliega el pipeline. Credenciales de la cuenta pipeline
cdk bootstrap --bootstrap-customer-key --cloudformation-execution-policies 'arn:aws:iam::aws:policy/AdministratorAccess' aws://<pipeline-account-xxx>/<region-xxx> --profile sso-pipeline

# credenciales de la cuenta de sandbox
cdk bootstrap --bootstrap-customer-key --cloudformation-execution-policies 'arn:aws:iam::aws:policy/AdministratorAccess' --trust <pipeline-account-xxx> aws://sandbox-account/<region> --profile sso-sandbox

# credenciales de la cuenta de prod
cdk bootstrap --bootstrap-customer-key --cloudformation-execution-policies 'arn:aws:iam::aws:policy/AdministratorAccess' --trust <pipeline-account-xxx> aws://prod-account/<region> --profile sso-prod

# Hacemos el deploy
cdk diff --profile sso-pipeline --all --app infrastructure/cdk.out
cdk deploy --profile sso-pipeline --all --app infrastructure/cdk.out
```


## Run project in local
Install the requirements on Mac and activate the env
```bash
python3 -m venv .env-lambdas
source .env-lambdas/bin/activate
pip install -r src/lambdas/requirements.txt
```

Run uvicorn server. It is important to set the ENVIRONMENT variable=local in order to use the local dynamodb instance.
```bash
cd src
ENVIRONMENT=local uvicorn lambdas.handler:app --reload
```

Configurate the local dynamodb instance
```bash
docker run -p 8000:8000 -d amazon/dynamodb-local
npm install -g dynamodb-admin
DYNAMO_ENDPOINT=http://localhost:8000 dynamodb-admin
```
Create the tables
TODO: adds local migrations to the local dynamodb


### Adds boto3 typping to Vs Code
https://pypi.org/project/boto3-stubs/


### Feature flags deployments
We implement CI/CD for this service, we use Trunk based development in order to do the deploys, if there are no much developers working at the same time, there is not problem to merge to the main branch then await the deploy into the sandbox environment finishes and does the manually test(only if there is another test that the unit test does not cover.), if we have success with the tests then we click on the manually step to approve the deploy to the production environment, but if we detect some issues on the tests that we did then we can do the fixes without worrying about stopping the changes/code of the others developers. But if more than one developer is working in the repository then we need to be able to do deploy using our feature branch where we are working, it is to say, When we do push of our feature branch we need something that creates a new infraestructure and makes the deploy of our code, with this we can easily do the test having an isolete box which has the last changes of the main branch, and when the branch is deleted it also deletes the infraestructure, and then we can send the merge to the main branch which raises all the pipeline up to the production deploy.
Here we have a article where it talks about how we can use github actions in order to resolve this problem.