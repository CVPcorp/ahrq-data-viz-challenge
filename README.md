# AHRQ Data Viz Challenge
<h3>**EC2 Deployment of Metabase with RDS**</h3>
<br>
<br>
<h5>**Purpose**:</h5>
	This documentation will cover how to deploy Metabase on an AWS EC2 instance with a separate RDS instance. <br>
	These directions were written to make setup as easy as possible for someone new to AWS. Not covered:
<br>
<br>
* You should have separate DB accounts for read-only and read-write users 
<br>
* We did not explicitly configure backups for the Metabase server. RDS snapshots should be sufficient. 
<br>
* If the server is restarted, you will need to manually restart Metabase as well.
<br>

<h5>**Prerequisites**:</h5>
- An AWS account
<br>
- DBeaver (or similar DB client)

<h5>**Installation**:</h5>
1.  Launch a t3.micro EC2 instance with Amazon Linux
<br>
2.  Create an RDS instance using a t2.small instance with a public IP, but not allowing external traffic (security group will be defined later).
<br>
3.	Create a security group for the EC2 instance allowing port 22 and port 3000 for your public IP address.
<br>
4.	Create a security group for the RDS instance allowing port 5432 in from the security group of the EC2 instance. You may also want to allow port 5432 inbound for the public IP addresses where any data uploads will come from (e.g. your laptop).
<br>
5.	SSH into the EC2 instance. Install the latest base and Java (version 11.0.2).
<br>
6.	Download the Metabase jar onto the EC2 instance using a wget command for the latest version. As of now that is: http://downloads.metabase.com/v0.33.3/metabase.jar 
<br>
7.	Open a PostgreSQL client like DBeaver. Create a new connection with your RDS credentials, establish a connection, and verify the database is available. 
<br>
8.	If the database connection works, setup environment variables on the EC2 instance so that Metabase will store the metadata in there instead of locally. You can see how to do this by scrolling down to the “PostgreSQL” section in the link:  https://www.metabase.com/docs/v0.12.0/operations-guide/running-the-metabase-jar-file.html
<br>
9.	Back in your SSH session to the EC2 instance, run Metabase in the background using the “screen” command, then running “java -jar metabase.jar”.
<br>
10.	Create a new database on RDS PostgreSQL called “sdohdb” and put an example table in it.
<br>
11.	Setup Metabase by opening your browser and going to the public DNS of the EC2 instance followed by “:3000”. The Metabase setup page will appear.
<br>
12. Create an admin account and setup the first data source pointing to and using the RDS credentials and pointing at the /sdohdb database. If a bunch of random tables you didn’t create appear, you probably pointed it to another database on the same RDS instance. In other words, isolate the Metabase tables by making the above data source DB different from the Metabase DB. We used the default “postgres” DB for Metabase and a new one called “sdohdb” as the data mart for the data source.
<br>
13. Click the “Ask a Question” button in the Metabase web UI and check if Metabase shows the sample table you created in step #10.

  