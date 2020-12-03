package cs.bham.ac.uk.assignment3;

import android.content.Context;
import android.net.Uri;
import android.os.Bundle;

import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


public class FavourFragment extends Fragment {

    private String Detail_Fave;
    private DetailAdapter fav_detailsAdpt;
    private RecyclerView.LayoutManager fav_layoutManager;
    private ArrayList<String> Faves = new ArrayList<String>();
    public FavourFragment() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {

        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_favour, container, false);
    }

    public void onViewCreated(View view, Bundle savedInstanceState) {

        //Log.i("Called","OnViewCreated Called");
        fav_detailsAdpt = new DetailAdapter(Faves);
        //RecyclerView fav_listView = (RecyclerView) findViewById(R.id.Fav_List);

        RecyclerView fav_listView = (RecyclerView) getActivity().findViewById(R.id.Fav_List);

        fav_layoutManager = new LinearLayoutManager(this.getContext());
        fav_listView.setLayoutManager(fav_layoutManager);
        fav_listView.setAdapter(fav_detailsAdpt);
        if (getActivity() instanceof MainActivity) {
            this.Detail_Fave = ((MainActivity) getActivity()).Favourite;
        }
        if (getActivity() instanceof FoodDetailActivity) {
            this.Detail_Fave = ((FoodDetailActivity) getActivity()).Favourite;
        }

        Log.i("Called Favourites",this.Detail_Fave);
        Faves.clear();
        String[] Temp = this.Detail_Fave.split(",");
        for (int i = 0; i < Temp.length;i++){
            Faves.add(Temp[i]);
        }
        //Faves = Arrays.asList(Detail_Fave.split(","));
        fav_detailsAdpt.notifyDataSetChanged();
    }

    @Override
    public void onResume(){
        super.onResume();
        if (getActivity() instanceof MainActivity) {
            this.Detail_Fave = ((MainActivity) getActivity()).Favourite;
        }
        if (getActivity() instanceof FoodDetailActivity) {
            this.Detail_Fave = ((FoodDetailActivity) getActivity()).Favourite;
        }
        fav_detailsAdpt.notifyDataSetChanged();
    }
    @Override
    public void onStart(){
        super.onStart();
        if (getActivity() instanceof MainActivity) {
            this.Detail_Fave = ((MainActivity) getActivity()).Favourite;
        }
        if (getActivity() instanceof FoodDetailActivity) {
            this.Detail_Fave = ((FoodDetailActivity) getActivity()).Favourite;
        }
        fav_detailsAdpt.notifyDataSetChanged();
    }


}
