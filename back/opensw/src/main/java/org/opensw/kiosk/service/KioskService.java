package org.opensw.kiosk.service;

import org.opensw.kiosk.entity.Menu;

import java.io.IOException;
import java.util.List;

public interface KioskService {
    List<Menu> getAllKiosks();
    public String readFileFromClassPath(String filename) throws IOException;
}
