package com.lnl.montorhome;

import android.os.Bundle;
import android.preference.PreferenceFragment;
import android.util.Log;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 03/04/16.
 */
public class SettingsFragment extends PreferenceFragment {

    String TAG = "SettingsFragment";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Log.d(TAG, "onCreeate called");
        // Load the preferences from XML resource
        addPreferencesFromResource(R.xml.preferences);

//        getFragmentManager().beginTransaction().replace(android.R.id.content, new SettingsFragment()).commit();
    }
}
