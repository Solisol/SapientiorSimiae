import java.util.Set;
import java.util.List;
import java.util.Map;
import java.util.HashSet;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.Scanner;
import java.io.Serializable;
import java.io.ObjectOutputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.FileInputStream;

public class DemoPlayer {
  public static void main(String[] args) throws Exception {
    Scanner sc = new Scanner(System.in);
    String roundType = sc.nextLine();
    String id = sc.nextLine();
    Monkey monkey;
    if (roundType.equals("INIT")) {
      monkey = new Monkey(id);
      monkey.init(sc);
    } else {
      monkey = Monkey.readFromCache(id);
      monkey.turn(sc);
    }
    sc.close();
    monkey.writeToCache();
  }
}

class Monkey implements Serializable {
  public static final long serialVersionUID = 0;

  static final String CACHE_PREFIX = "cache_";

  final String id;
  // Position
  int x, y;
  // Toplists
  int topDecade;
  Set<String> topTracks = new HashSet<String>(), 
              topAlbums = new HashSet<String>(), 
              topArtists = new HashSet<String>(), 
              dislikedArtists = new HashSet<String>();
  // URI dictionary
  Map<String, Track> knownURIs = new HashMap<String, Track>();
  // Tracks
  List<Track> unknownTracks;
  List<Track> knownTracks;
  int turn, turnLimit;
  int width, height;
  int remainingCapacity, remainingExecutionTime, boostCooldown;
  String[][] level;

  Monkey(String id) {
    this.id = id;
  }

  void init(Scanner sc) {
    parseInit(sc);
    parseToplists(sc);
  }

  void turn(Scanner sc) {
    parseTurn(sc);
    parseMetadata(sc);
    parseLevel(sc);
  }

  void parseInit(Scanner sc) {
    width = sc.nextInt();
    height = sc.nextInt();
    turnLimit = sc.nextInt();
    level = new String[width][height];
  }

  void parseToplists(Scanner sc) {
    List<Integer> decades = new ArrayList<Integer>();
    // Top tracks
    int numTracks = sc.nextInt();
    sc.nextLine();
    for (int i = 0; i < numTracks; i++) {
      String entry = sc.nextLine();
      // 0:[track],1:[album],2:[artist],3:[year]
      String[] parts = entry.split(",");
      topTracks.add(parts[0]);
      int decade = Util.toDecade(Integer.parseInt(parts[3]));
      decades.add(decade);
    }
    // Top albums
    int numAlbums = sc.nextInt();
    sc.nextLine();
    for (int i = 0; i < numAlbums; i++) {
      String entry = sc.nextLine();
      // 0:[album],1:[artist],2:[year]
      String[] parts = entry.split(",");
      topAlbums.add(parts[0]);
      int decade = Util.toDecade(Integer.parseInt(parts[2]));
      decades.add(decade);
    }
    // Top decade
    topDecade = Util.getPopularElement(
        decades.toArray(new Integer[decades.size()]));
    // Top artists
    int numArtists = sc.nextInt();
    sc.nextLine();
    for (int i = 0; i < numArtists; i++) {
      // 0:[artist]
      String entry = sc.nextLine();
      topArtists.add(entry);
    }
    // Disliked artists
    int numDislikedArtists = sc.nextInt();
    sc.nextLine();
    for (int i = 0; i < numDislikedArtists; i++) {
      // 0:[artist]
      String entry = sc.nextLine();
      dislikedArtists.add(entry);
    }
  }

  void parseTurn(Scanner sc) {
    turn = sc.nextInt();
    remainingCapacity = sc.nextInt();
    remainingExecutionTime = sc.nextInt();
    boostCooldown = sc.nextInt();
  }

  void parseMetadata(Scanner sc) {
    int numResults = sc.nextInt();
    sc.nextLine();
    for (int i = 0; i < numResults; i++) {
      String metadata = sc.nextLine();
      Track knownTrack = Track.fromMetadata(metadata);
      // 0:[uri],1:[[track],[album],[artist],[year]]
      String[] parts = metadata.split(",", 1);
      knownURIs.put(parts[0], knownTrack);
    }
  }

  void parseLevel(Scanner sc) {
    unknownTracks = new ArrayList<Track>();
    knownTracks = new ArrayList<Track>();
    for (int y = 0; y < height; y++) {
      String row = sc.nextLine();
      String[] cells = row.split(",");
      for (int x = 0; x < width; x++) {
        level[x][y] = cells[x];
        if (Util.isURI(cells[x])) {
          String uri = cells[x];
          if (!knownURIs.containsKey(uri)) {
            unknownTracks.add(new Track(uri).place(x, y));
          } else {
            knownTracks.add(knownURIs.get(uri).copy().place(x, y)); 
          }
        }
      }
    }
  }

  void writeToCache() throws Exception {
    ObjectOutputStream out = 
      new ObjectOutputStream(new FileOutputStream(CACHE_PREFIX + id));
    out.writeObject(this);
    out.close();
  }

  static Monkey readFromCache(String id) throws Exception {
    ObjectInputStream in =
      new ObjectInputStream(new FileInputStream(CACHE_PREFIX + id));
    Monkey monkey = (Monkey) in.readObject();
    in.close();
    return monkey;
  }

}

class Track implements Cloneable, Serializable {
  public static final long serialVersionUID = 0;

  String uri, name, album, artist, year;
  int x, y;
  int value;

  Track (String uri) {
    this.uri = uri;
  }

  static Track fromMetadata(String metadata) {
    // 0:[uri],1:[name],2:[album],3:[artist],4:[year]
    String[] parts = metadata.split(","); 
    Track track = new Track(parts[0]);
    track.name = parts[1];
    track.album = parts[2];
    track.artist = parts[3];
    track.year = parts[4];
    return track;
  }

  Track place(int x, int y) {
    this.x = x;
    this.y = y;
    return this;
  }

  Track copy() {
    Track copy = new Track(uri);
    copy.name = name;
    copy.album = album;
    copy.artist = artist;
    copy.year = year;
    copy.value = value;
    return copy;
  }

  @Override public int hashCode() { return uri.hashCode(); }
}

class Util {
  /** 
  * http://stackoverflow.com/questions/8545590/java-find-the-most-popular-element-in-int-array
  */
  static int getPopularElement(Integer[] a) {
    int count = 1, tempCount;
    int popular = a[0];
    int temp = 0;
    for (int i = 0; i < (a.length - 1); i++) {
      temp = a[i];
      tempCount = 0;
      for (int j = 1; j < a.length; j++) {
        if (temp == a[j])
          tempCount++;
      }
      if (tempCount > count) {
        popular = temp;
        count = tempCount;
      }
    }
    return popular;
  }

  static int toDecade(int year) {
    return (year % 100) / 10;
  }

  static boolean isURI(String s) {
    return s.length() == 36 && s.substring(0, 14).equals("spotify:track:");
  }
}
