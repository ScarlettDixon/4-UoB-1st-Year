package cs.bham.ac.uk.assignment3;

import android.content.Context;
import android.net.Uri;
import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.RadioGroup;


public class PreferFragment extends Fragment {

    //View selectedRadio;
    //RadioGroup meal = (RadioGroup)findViewById(R.id.radioGroup);
    //radio
    RadioButton upButton;
    View view;

    public PreferFragment() {
        // Required empty public constructor
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        //upButton = (RadioButton) view.findViewById(R.id.Pref_non);
        //upButton.setOnClickListener(this);
        return inflater.inflate(R.layout.fragment_prefer, container, false);

    }

    public void onViewCreated() {
        RadioButton nonbutt = getView().findViewById(R.id.Pref_non);
    }


}
