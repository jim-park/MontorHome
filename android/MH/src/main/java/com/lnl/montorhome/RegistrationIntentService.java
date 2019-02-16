package com.lnl.montorhome;

import android.app.IntentService;
import android.content.Intent;
import android.util.Log;

import com.google.android.gms.gcm.GoogleCloudMessaging;
import com.google.android.gms.iid.InstanceID;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 29/2/2559.
 */
public class RegistrationIntentService extends IntentService {
    String TAG = "RegIntentService";
    String token = "";

    public RegistrationIntentService() {
        super("MyIntentService");
    }

    @Override
    public void onHandleIntent(Intent intent) {

        Log.i(TAG, " - service started");
        InstanceID instanceID = InstanceID.getInstance(this);
        try {
            String tmp = getString(R.string.gcm_defaultSenderId);
            Log.d(TAG, "gcm SenderID: " + tmp);
            token = instanceID.getToken(tmp, GoogleCloudMessaging.INSTANCE_ID_SCOPE, null);
            Log.d(TAG, "gcm token: " + token);
        } catch (Exception e) {
            Log.e(TAG, "Failed to getToken - e: " + e);
        }

        postData("id="+token);
        // Send token to WebServer
        //if (token != null) {
        //}
        Log.d(TAG, " - service stopped");
    }

    public static void postData(String token) {
        String TAG = "postData";
        URL url;
        HttpURLConnection connection = null;

        try {
            // Create connection
            url = new URL("http://192.168.43.220/api.php");
            Log.d(TAG, "connecting ");
            connection = (HttpURLConnection)url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            connection.setFixedLengthStreamingMode(token.getBytes().length);
            connection.setRequestProperty("Content-Language", "en-US");
            connection.setUseCaches(false);
            connection.setDoInput(true);
            connection.setDoOutput(true);

            Log.d(TAG, "Send Request: " + token);
            // Send request
            DataOutputStream wr = new DataOutputStream(connection.getOutputStream());
            wr.writeBytes(token);
            wr.flush();
            wr.close();


            // Get Response
            InputStream is = connection.getInputStream();
            BufferedReader rd = new BufferedReader(new InputStreamReader(is));
            String line;
            StringBuffer response = new StringBuffer();

            while((line = rd.readLine()) != null) {
                response.append(line);
            }
            Log.i(TAG, "response: " + response.toString());
            rd.close();

            // TODO Validate response and do backing off retries if required

        } catch (Exception e){
            e.printStackTrace();
            Log.e(TAG, e.toString());
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }
}
