# 1. PostgreSQL
## 1.1 install
```bash
service <firewalld/iptables> stop
yum install -y postgresql-server

```
## 1.2 single node
### init
```bash
postgresql-setup initdb
# this command will generate DB files under default directory: ${PGDATA}
# you can also specify other directory as ${PGDATA}
```
### pg_hba.conf
```bash
vim ${PGDATA}/pg_hba.conf
```
```ini
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             0.0.0.0/0               trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
```
- METHOD: peer / md5(connection requires password verification) / trust

### postgresql.conf
```bash
vim ${PGDATA}/postgresql.conf
```
```ini
listen_addresses = '*'
```
### start & connect
```bash
service postgresql start
psql -h localhost -p 5432 -U postgres

# you can also try below CMD to start postgresql-server
su - postgres -c "pg_ctl start -D ${PGDATA}"
su - postgres -c "postgres -D ${PGDATA}" # daemon
```
## 1.3 master-slave mode
|  | master(primary) | slave(standby) |
| --- | --- | --- |
| read write | RW | RO |
| select pg_is_in_recovery(); | f | t |
| select * from pg_stat_replication; | several record with state: streaming | no record |
### master node: pg_hba.conf
```bash
vim ${PGDATA}/pg_hba.conf
```
```ini
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     postgres                                trust
host    replication     postgres        0.0.0.0/0               trust
host    replication     postgres        ::1/128                 trust
```
### master node: postgresql.conf
```bash
vim ${PGDATA}/postgresql.conf
```
```ini
wal_level = logical
wal_log_hints = on
# set max_wal_senders > 0
max_wal_senders = 10
hot_standby = on
```
### master node: restart
```bash
service postgresql restart
```
### slave node: init
```bash
su postgres -c 'pg_basebackup -D ${PGDATA} -h <master node IP> -p 5432 -U postgres -Xs'
```
### slave node: recovery.conf
```bash
vim ${PGDATA}/recovery.conf
```
```ini
standby_mode = on
recovery_target_timeline = latest
primary_conninfo = 'host=<master node IP> port=5432 user=postgres'
```
### slave node: start & connect
```bash
service postgresql start
psql -h localhost -p 5432 -U postgres
```
### check: @master-node
```bash
psql -h localhost -p 5432 -U postgres
```
```text
postgres=# select client_addr,state from pg_stat_replication;
  client_addr  |   state   
---------------+-----------
 192.168.56.61 | streaming
 192.168.56.62 | streaming
```
```text
postgres=# select pg_is_in_recovery();
 pg_is_in_recovery 
-------------------
 f
```
```text
postgres=# select txid_current_snapshot();
 txid_current_snapshot 
-----------------------
 548:548: 
```
### check: @slave-node
```bash
psql -h localhost -p 5432 -U postgres
```
```text
postgres=# select client_addr,state from pg_stat_replication;
 client_addr | state 
-------------+-------
(0 行记录)
```
```text
postgres=# select pg_is_in_recovery();
 pg_is_in_recovery 
-------------------
 t
```
```text
postgres=# select txid_current_snapshot();
 txid_current_snapshot 
-----------------------
 548:548: 
```
## 1.4 hot switch
### promote slave to master
```bash
su - postgres -c "pg_ctl promote -D ${PGDATA}"
```
### configure old master or other slave to recover from new master
- create or edit recovery.conf under ${PGDATA}, set "host" refer to new master, then restart pgsql-server

```bash
vim ${PGDATA}/recovery.conf
```
```ini
standby_mode = on
recovery_target_timeline = latest
primary_conninfo = 'host=<new master node IP> port=5432 user=postgres'
```
```bash
service postgresql restart
# or: su - postgres -c "pg_ctl restart -D ${PGDATA}"
# in some version(e.g. pg-9.2), you may need to sync timeline first:
# $ pg_rewind  --target-pgdata=${PGDATA} --source-server='host=<master IP> port=5432 user=postgres'
```


# 2. pgpool-II
## 2.1 config
### pgpool.conf
```bash
vim /etc/pgpool-II/pgpool.conf
```
```ini
listen_addresses = '*'

backend_hostname0 = <pgsql server node-0 IP>
backend_port0 = 5432
backend_weight0 = 1
backend_data_directory0 = <pgsql server node-0 ${PGDATA}>
backend_flag0 = 'ALLOW_TO_FAILOVER'

backend_hostname1 = <pgsql server node-1 IP>
backend_port1 = 5432
backend_weight1 = 1
backend_data_directory1 = <pgsql server node-1 ${PGDATA}>
backend_flag1 = 'ALLOW_TO_FAILOVER'

backend_hostname2 = <pgsql server node-2 IP>
backend_port2 = 5432
backend_weight2 = 1
backend_data_directory2 = <pgsql server node-2 ${PGDATA}>
backend_flag2 = 'ALLOW_TO_FAILOVER'

enable_pool_hba = on
replication_mode = off
load_balance_mode = on
master_slave_mode = on
master_slave_sub_mode = 'stream'
sr_check_user = 'postgres'
follow_master_command = 'bash /root/pg/fail.sh after_failover %d %h %p %D %m %H %M %P %r %R >> /tmp/fail.log'

health_check_period = 1
health_check_timeout = 3
health_check_user = 'postgres'

failover_command = 'bash /root/pg/fail.sh failover %d %h %p %D %m %H %M %P %r %R >> /tmp/fail.log'
failback_command = 'bash /root/pg/fail.sh failback %d %h %p %D %m %H %M %P %r %R >> /tmp/fail.log'

use_watchdog = on
trusted_servers = '<self IP>,<pgpool node-0 IP>,<pgpool node-1 IP>'
ping_path = '/usr/bin'
wd_hostname = <self IP>

delegate_IP = <VIP>
ifconfig_path = '/usr/sbin'
if_up_cmd = 'ifconfig enp0s8:0 inet $_IP_$ netmask 255.255.255.0'
if_down_cmd = 'ifconfig enp0s8:0 down'

wd_lifecheck_method = 'heartbeat'
heartbeat_destination0 = <pgpool node-0 IP>
heartbeat_destination_port0 = 9694
heartbeat_device0 = 'enp0s8'
heartbeat_destination1 = <pgpool node-1 IP>
heartbeat_destination_port1 = 9694
heartbeat_device1 = 'enp0s8'

other_pgpool_hostname0 = <pgpool node-0 IP>
other_pgpool_port0 = 9999
other_wd_port0 = 9000
other_pgpool_hostname1 = <pgpool node-1 IP>
other_pgpool_port1 = 9999
other_wd_port1 = 9000

```
### /root/pg/fail.sh
```bash
echo === $(date) ===

echo node id: $2
echo host name: $3
echo port number: $4
echo database cluster path: $5
echo new master node id: $6
echo hostname of the new master node: $7
echo old master node id: $8
echo old primary node id: $9
echo new master port number: ${10}
echo new master database cluster path: ${11}

step=$1
node_id=$2
node_ip=$3
old_primary_id=$9
primary_ip=$7
echo ${step}

ssh_nopass="sshpass -p 1 ssh -o StrictHostKeyChecking=no"

case ${step} in
failover )
echo failover
if [ ${node_id} == ${old_primary_id} ]
then
${ssh_nopass} ${primary_ip} bash /root/pg/promote.sh
fi
;;
after_failover )
echo after_failover
${ssh_nopass} ${node_ip} bash /root/pg/start-slave.sh ${primary_ip}
pcp_attach_node 5 localhost 9898 postgres postgres ${node_id}
;;
failback )
echo failback
#${ssh_nopass} ${node_ip} bash /root/pg/start-slave.sh ${primary_ip}
;;
esac

echo ==================================================
```
### pcp.conf
- register pcp account used by "pcp CMD"
- below is a example: username 'postgres', password 'postgres'

```bash
echo postgres:$(pg_md5 postgres) >> /etc/pgpool-II/pcp.conf
vim /etc/pgpool-II/pcp.conf
```
```text
postgres:e8a48653851e28c69d0506508fb27fc5
```
## 2.2 check via psql
```bash
psql -h <pgpool VIP> -p 9999 -U postgres
```
```text
postgres=# show pool_nodes;
 node_id |   hostname    | port | status | lb_weight |  role   
---------+---------------+------+--------+-----------+---------
 0       | 192.168.56.61 | 5432 | 2      | 0.333333  | standby
 1       | 192.168.56.62 | 5432 | 2      | 0.333333  | standby
 2       | 192.168.56.63 | 5432 | 2      | 0.333333  | primary
```
- status: 1(newly added) / 2(active) / 3(inactive)

## 2.3 pcp CMD
- hostname: pgpool node IP, VIP of pgpool cluster is strongly suggested
- port: configured in pgpool.conf, default is 9898
- username: refer to username in pcp.conf
- password: refer to password in pcp.conf
- nodeID: node-x in pgpool.conf, e.g. 0, 1, 2

```bash
# get backend postgresql-server node info
pcp_node_count --help
pcp_node_info --help
# get watch dog info
pcp_watchdog_info --help
# after an offline postgresql-server back online, and which is correctly recover to good condition
# use below command to notify pgpool cluster
pcp_attach_node --help
```

