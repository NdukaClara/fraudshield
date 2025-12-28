# My Wild Ride Adding Spark to Docker (and Installing It Locally) for FraudShield IQ

If you’ve ever tried to add Spark to your project, you probably know it’s not always smooth sailing. I recently went through the whole rollercoaster while working on my FraudShieldIQ project (Read about it here https://www.linkedin.com/posts/clara-nduka_fraudshieldiq-real-time-transaction-activity-7388488381904699393-Vif8?utm_source=share&utm_medium=member_desktop&rcm=ACoAAC15o40Bl-96X2OyXhyFrYmLYWry2tXkehE), and I figured I’d share all the errors, weird messages, and head-scratching moments so I won’t have to live through it again—and maybe so someone else can learn from my mistakes.

It all started when I decided to add Spark to Docker. I wanted a Spark master and worker running alongside my existing Kafka and Postgres setup. I wrote my `docker-compose.yml`, feeling pretty confident, and then… nothing worked. Docker kept failing to pull images, throwing errors like `manifest unknown` or timing out while waiting for headers.

```yml
spark-master:
  image: bitnami/spark:3.5
  container_name: spark-master
  environment:
    - SPARK_MODE=master
  ports:
    - "7077:7077"

spark-worker:
  image: bitnami/spark:3.5
  container_name: spark-worker
  environment:
    - SPARK_MODE=worker
    - SPARK_MASTER_URL=spark://spark-master:7077
```

At first, I couldn’t figure out why. I tried pulling individual images like `hello-world` or `bitnami/spark:3.5.2`, but each attempt just timed out. Curl couldn’t even resolve `ghcr.io`. I restarted Docker, restarted my Mac, pruned networks, removed Docker configs, factory-reset Docker Desktop multiple times… and still, every `docker pull` command just stared back at me with the same timeout errors.

Eventually, I realized I had forgotten I was using a VPN. The VPN was routing Docker traffic through a proxy (`docker.internal:3128`) that I didn’t want, which was why nothing could reach Docker Hub. Once I disabled the VPN and reset Docker, things started behaving better, but not completely smooth. Some images were still misbehaving, like certain Bitnami Spark versions not existing in the registry.

```bash
docker pull bitnami/spark:latest
docker pull bitnami/spark:3.5.3
```

Every attempt failed. Either Docker said the manifest wasn’t found or the image didn’t exist. I even tried specific versions. No luck. All the while, I was seeing errors like:

```bash
Error response from daemon: manifest for bitnami/spark:latest not found: manifest unknown
```

Frustrated, I switched to the official Apache Spark images. Pulled `apache/spark:3.5.0`, and finally, the pull worked:

```bash
docker pull apache/spark:3.5.0
Digest: sha256:...
Status: Image is up to date for apache/spark:3.5.0
```

Great, except now the containers still had the old names and environment variables I’d set for Bitnami Spark. Apache Spark didn’t recognize those environment settings, so when I tried to start the Spark master container, it would exit immediately. Running `docker ps -a` showed:

```bash
apache/spark:3.5.0  Exited (0) ...
```

I had to go back and adjust the environment to what Apache Spark actually expects.

 *********screenshot of updated spark part of docker-compose.yml**********

 Once I did that and recreated the containers, everything finally started. The Spark master UI on localhost:8080 loaded without a hitch. 

 *********screenshot of spark on localhost**********

Next came running PySpark locally. I immediately ran into Java issues. PySpark kept complaining:

```bash
The operation couldn’t be completed. Unable to locate a Java Runtime.
```

Even though I had Java 25 installed. Turns out Spark didn’t like Java 25. I had to install Java 17, set `JAVA_HOME` correctly, and make sure Python picked up the right version. 

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"
```


After that, creating a Spark session finally worked:

 *********screenshot of spark session created successfully**********

 Along the way, there were warnings about my hostname resolving to a loopback address, restricted Java modules, native Hadoop libraries missing-—all the little things that make you go “oh, okay, fine, I’ll ignore it for now.”

Anyway, the point of this post isn’t to give instructions. It’s just to highlight the messiness: Docker timeouts, proxy issues, manifests not found, containers exiting, Java version headaches. Restarting Docker, my computer, switching VPNs on and off, pulling different images, downgrading Java, was all part of the process.

If you’re trying to add Spark to Docker and run it locally, just know that chaos is guaranteed. But I hope this post helps you to sail smoothly.