package com.elavirint.pipoprint;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.recyclerview.widget.RecyclerView;

import com.elavirint.pipoprint.utils.DataManager;

import java.util.ArrayList;

public class BluetoothDeviceCardAdapter extends RecyclerView.Adapter<BluetoothDeviceCardAdapter.ViewHolder> {

    private final ArrayList<BluetoothDevice> bluetoothDeviceList = new ArrayList<>();

    private int mSelectedPosition = RecyclerView.NO_POSITION;

    private Context context;

    public BluetoothDevice getSelected() {
        if (mSelectedPosition == RecyclerView.NO_POSITION) {
            return null;
        } else {
            return bluetoothDeviceList.get(mSelectedPosition);
        }
    }

    public BluetoothDeviceCardAdapter() {

    }

    public void addDevice(BluetoothDevice newDevice) {
        for (BluetoothDevice device : bluetoothDeviceList) {
            if (device.getAddress().equals(newDevice.getAddress())) {
                return;
            }
        }

        bluetoothDeviceList.add(newDevice);
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        public CardView cardView;
        public TextView titleTextView;
        public TextView descriptionTextView;

        public ViewHolder(View itemView) {
            super(itemView);

            cardView = itemView.findViewById(R.id.cardView);
            titleTextView = itemView.findViewById(R.id.titleTextView);
            descriptionTextView = itemView.findViewById(R.id.descriptionTextView);
        }
    }



    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        context = parent.getContext();
        View view = LayoutInflater.from(context).inflate(R.layout.card_item_layout, parent, false);

        return new ViewHolder(view);
    }

    @SuppressLint("MissingPermission")
    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        BluetoothDevice bluetoothDevice = bluetoothDeviceList.get(position);

        holder.titleTextView.setText(bluetoothDevice.getName());
        holder.descriptionTextView.setText(bluetoothDevice.getAddress());

        holder.itemView.setOnClickListener(view -> {
            int adapterPosition = holder.getAdapterPosition();

            if (adapterPosition != RecyclerView.NO_POSITION) {
                setSelectedPosition(holder, adapterPosition); // update the selected position
            }
        });

        if (mSelectedPosition == position) {
            holder.cardView.setCardBackgroundColor(context.getColor(R.color.purple_500));
            holder.titleTextView.setTextColor(context.getColor(R.color.white));
            holder.descriptionTextView.setTextColor(context.getColor(R.color.white));
        }
    }

    public void setSelectedPosition(ViewHolder holder, int position) {
        DataManager.getInstance().selectBluetoothDevice(position);

        int oldSelectedPosition = mSelectedPosition;
        mSelectedPosition = position;
        notifyItemChanged(oldSelectedPosition);
        notifyItemChanged(mSelectedPosition);
    }

    @Override
    public int getItemCount() {
        return bluetoothDeviceList.size();
    }
}
