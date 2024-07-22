package com.elavirint.pipoprint;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;

public class ListViewItemAdapter extends ArrayAdapter<ListViewItem> {

    private ListViewItem[] items;

    public ListViewItemAdapter(@NonNull Context context, ListViewItem[] items) {
        super(context, 0, items);

        this.items = items;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(
                    R.layout.list_item, parent, false
            );
        }

        ListViewItem currentItem = items[position];

        ImageView itemIcon = convertView.findViewById(R.id.itemIcon);
        itemIcon.setImageResource(currentItem.icon);

        TextView itemText = convertView.findViewById(R.id.itemText);
        itemText.setText(currentItem.text);

        return convertView;
    }
}
