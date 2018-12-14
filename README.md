# Scalr Webhook: Approvals

This is a simple web-based approval system built to showcase Scalr's built-in Approval workflow support.  Requests are presented via a web UI, with the option to provide a message passed back to the Scalr server along with the approval or denial.

### Pre-Requisites

##### Repository Packages:
```
python
python-pip
redis-server
```

##### Python Modules:
```
flask
redis
requests
pusher    *OPTIONAL*
```

### Create Endpoint in Scalr

In order for Scalr to communicate with the approval system, an Endpoint needs to be created.  From the Scalr menu, highlight Integration Hub, and then select Endpoints.  Choose a friendly name for the endpoint and provide a URL of `http://<server-ip>:<port>/approve`.  After saving the Endpoint, a signing key is generated. Copy this key into `approvals.py` on Line 14 in the place of `<SCALR_ENDPOINT_KEY>`.


### Enabling Optional Pusher functionality

To obtain real-time updates on the web client whenever a change is made to a request stored in Redis, Pusher functionality has been built in.  In order to activate it, it is first necessary to create an account with [Pusher]( https://dashboard.pusher.com/accounts/sign_up).  

Once you create an account and an App within Pusher, it is necessary to uncomment the Pusher code in the `approvals.py and `templates/list.html` files.

##### approvals.py
```
Line 16-22
   #pusher_client = pusher.Pusher(
   #  app_id='<PUSHER_APP_ID>,
   #  key='<PUSHER_KEY>',
   #  secret='<PUSHER_SECRET>',
   #  cluster='<PUSHER_CLUSTER>',
   #  ssl=True
   #)
Line 76
   #pusher_client.trigger('live-approve', 'redis-update', {'message': 'Data changed'})
Line 117
   #pusher_client.trigger('live-approve', 'redis-update', {'message': 'Data changed'})
```

##### templates/list.html
```
Line 26-36
   // Pusher.logToConsole = true;

   // var pusher = new Pusher('<PUSHER_KEY>', {
   //    cluster: '<PUSHER_CLUSTER>',
   //    forceTLS: true
   // });

   // var channel = pusher.subscribe('live-approve');
   // channel.bind('redis-update', function() {
   //   $scope.showlist();
   // });

Once the appropriate code has been uncommented, it is necessary to copy the appropriate data from the Pusher app you created.  Update the variables with `<PUSHER_APP_ID>`, `<PUSHER_KEY>`, `<PUSHER_SECRET>`, and `<PUSHER_CLUSTER>` in both the `approvals.py` and the `templates/list.html` files.

### Starting your App

Once the necessary configurations have been handled, the application can be started by running the following from the directory contaning `approvals.py`:

`FLASK_APP=approvals.py flask run --host=0.0.0.0 --port=<port>`


