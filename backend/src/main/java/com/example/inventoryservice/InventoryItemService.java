package com.example.inventoryservice;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class InventoryItemService {
    @Autowired
    private InventoryItemRepository repository;

    public List<InventoryItem> getAllItems() {
        return repository.findAll();
    }

    public Optional<InventoryItem> getItemById(Long id) {
        return repository.findById(id);
    }

    public InventoryItem createItem(InventoryItem item) {
        item.setUpdatedAt(LocalDateTime.now());
        return repository.save(item);
    }

    public Optional<InventoryItem> updateItem(Long id, InventoryItem updated) {
        return repository.findById(id).map(item -> {
            item.setName(updated.getName());
            item.setSku(updated.getSku());
            item.setQuantity(updated.getQuantity());
            item.setLocation(updated.getLocation());
            item.setUpdatedAt(LocalDateTime.now());
            return repository.save(item);
        });
    }

    public void deleteItem(Long id) {
        repository.deleteById(id);
    }
}
