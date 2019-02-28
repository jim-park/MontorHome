package com.lnl.montorhome;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 28/01/19.
 */

public class FetchDataTask extends AsyncTask<String, Void, FetchDataTask.Wrapper> {

    String TAG = "FetchDataTask";

    class Wrapper
    {
        String data = "";
        String type = "";
    }
    private AsyncResponse delegate = null;
    private Context appContext;
    private Wrapper wrapper =new Wrapper();

    public FetchDataTask(Context context, AsyncResponse caller) {
        delegate = caller;
        appContext = context;
    }

    public interface AsyncResponse {
        void processFinish(Wrapper output);
    }

    @Override
    protected void onPostExecute(Wrapper result) {
        delegate.processFinish(result);
    }

    @Override
    protected Wrapper doInBackground(String... params) {

        wrapper.type = params[0];
        HttpURLConnection urlConnection;
        URL url;
        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(appContext);

        try {
            // Retrieve the API server local WLAN network address info from preferences.
            String api_addr = prefs.getString("key_api_lan_server_addr", "NOTFOUND");

            // Change the API server url to the cloud address if we are not on the system WLAN.
            if(!NetworkChangeBroadcastReceiver.connectedToSystemLAN())
                api_addr = prefs.getString("key_api_cloud_server_addr", "NOTFOUND");

            // Build, log, open, the API url.
            url = new URL("http://" + api_addr + "/" + params[0]);
            Log.d("INFO", "Opening URL: " + url);
            urlConnection = (HttpURLConnection) url.openConnection();

            // Read response.
            try {
                BufferedReader bufferReader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
                StringBuilder stringBuilder = new StringBuilder();
                String line;
                while((line = bufferReader.readLine()) != null) {
                    stringBuilder.append(line);
                }
                bufferReader.close();
                wrapper.data = stringBuilder.toString();
                return wrapper;
            }
            finally {
                urlConnection.disconnect();
            }
        }
        catch (Exception e) {
            Log.e("ERROR", e.getMessage());
            wrapper.data = "0.0";
            return wrapper;
        }

    }
}
