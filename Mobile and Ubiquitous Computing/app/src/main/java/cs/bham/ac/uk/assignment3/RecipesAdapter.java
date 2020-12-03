package cs.bham.ac.uk.assignment3;

import android.content.Intent;
import android.util.TypedValue;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;

public class RecipesAdapter extends RecyclerView.Adapter<RecipesAdapter.ViewHolder>{
    private ArrayList<RecipeViewer> recipes;
    private String Favourites;
    public static class ViewHolder extends RecyclerView.ViewHolder {
        public TextView textView;
        public ViewHolder(TextView v) {
            super(v);
            textView = v;
        }
    }
    public RecipesAdapter(ArrayList<RecipeViewer> recipes) {
        this.recipes = recipes;
    }
    @Override
    public RecipesAdapter.ViewHolder onCreateViewHolder(ViewGroup parent, int
            viewType) {
        ViewHolder vh = new ViewHolder(new TextView(parent.getContext()));
        vh.textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20f);
        return vh;
    }
    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, final int position) {
        holder.textView.setText(recipes.get(position).toName());
        holder.textView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent( v.getContext(), FoodDetailActivity.class);
                intent.putExtra("RecID", recipes.get(position).getRec_ID());
                intent.putExtra("name", recipes.get(position).getName());
                v.getContext().startActivity(intent);
            }
        });
    }
    @Override
    public int getItemCount() {
        return recipes.size();
    }
}

