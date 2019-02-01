package com.lnl.montorhome;

import android.os.AsyncTask;
import android.util.Log;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class FetchDataTask extends AsyncTask<String, Void, FetchDataTask.Wrapper> {

    class Wrapper
    {
        String data = "";
        String type = "";
    }
    private static final String API_URL = "http://192.168.8.102:5000/";
    public AsyncResponse delegate = null;
    private Wrapper wrapper =new Wrapper();

    public FetchDataTask(AsyncResponse caller) {
        delegate = caller;
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

        try {
            URL url = new URL(API_URL + params[0]);
            Log.i("INFO", "URL: " + url);

            HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
            try {
                BufferedReader bufferReader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
                StringBuilder stringBuilder = new StringBuilder();
                String line;
                while((line = bufferReader.readLine()) != null) {
                    Log.i("INFO", "read line: " + line);
                    stringBuilder.append(line);
                }
                bufferReader.close();
                wrapper.data = stringBuilder.toString();
                wrapper.type = params[0];
                return wrapper;
            }
            finally {
                urlConnection.disconnect();
            }
        }
        catch (Exception e) {
            Log.e("ERROR", e.getMessage());
            return null;
        }

    }
}
