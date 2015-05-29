#### Getting started

Example parsing [Dockerfile](https://github.com/docker-library/cassandra/blob/master/2.1/Dockerfile) project Cassandra (in json-format):

    {
      "workdir": {
        "/": {
          "root": {
            "run": [
              "apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys 514A2AD631A57A16DD0047EC749D6EEC0353B12C",
              "echo 'deb http://www.apache.org/dist/cassandra/debian 21x main' >> /etc/apt/sources.list.d/cassandra.list",
              "apt-get update && apt-get install -y cassandra=\"$CASSANDRA_VERSION\" && rm -rf /var/lib/apt/lists/*",
              "sed -ri ' s/^(rpc_address:).*/1 0.0.0.0/; ' \"$CASSANDRA_CONFIG/cassandra.yaml\""
            ],
            "copy": [
              {
                "dest": "/docker-entrypoint.sh",
                "src": "docker-entrypoint.sh"
              }
            ],
            "entrypoint": [
              "/docker-entrypoint.sh"
            ],
            "cmd": [
              [
                "cassandra",
                "-f"
              ]
            ]
          }
        }
      },
      "from": {
        "detail": {
          "image": "debian",
          "tag": "jessie"
        },
        "full_name": "debian:jessie"
      },
      "env": {
        "CASSANDRA_VERSION": "2.1.5",
        "CASSANDRA_CONFIG": "/etc/cassandra"
      },
      "volume": [
        "/var/lib/cassandra/data"
      ],
      "expose": [
        7000,
        7001,
        7199,
        9042,
        9160
      ]
    }

#### Where can I use the library?

* Create a utility that will optimize Dockerfile
* In the analysis of a large number of Dockerfile
* Checking commands that will be launched in the container
* ... also in other practical or research purposes

#### Errors and bugs

If you are working with a library errors, [create](https://github.com/eg0r/dockerfile-parser/issues/new) issue, so it can be corrected.