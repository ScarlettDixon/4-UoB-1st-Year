package cs.bham.ac.uk.assignment3;

import android.content.Intent;
import android.util.TypedValue;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;

public class DetailAdapter extends RecyclerView.Adapter<DetailAdapter.ViewHolder>{
    //private ArrayList<RecipeViewer> details;
    private ArrayList<String> details;
    public static class ViewHolder extends RecyclerView.ViewHolder {
        public TextView textView;
        public ViewHolder(TextView v) {
            super(v);
            textView = v;
        }
    }
    //public DetailAdapter(ArrayList<RecipeViewer> details) { this.details = details; }
    public DetailAdapter(ArrayList<String> details) {
        this.details = details;
    }
    @Override
    public DetailAdapter.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        ViewHolder vh = new ViewHolder(new TextView(parent.getContext()));
        vh.textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15f);
        return vh;
    }
    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, final int position) {
        holder.textView.setText(details.get(position));
    }
    @Override
    public int getItemCount() {
        return details.size();
    }
}