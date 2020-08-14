from mip import Model, xsum, minimize, BINARY
from mip.constants import OptimizationStatus

if __name__=="__main__":
    import sys
    target = float(sys.argv[1])

    tracks = [
        ('Marseille (feat. Abd Al Malik)', '6RkGrUeBntd8PSKBdLlt7q', 443480),
        ('My Funny Valentine', '3CfW6EJvfEkYg5YX2RgcAR', 636746),
        ('Breathe', '6nGNzqlHTKugpRWkXrZkPC', 447000),
        ('My Funny Valentine', '3g2FFxa9Z0fdE8lThRtHyi', 540467),
        ('My Funny Valentine', '4l9hml2UCnxoNI3yCdL1BW', 141133),
        ('My Funny Valentine', '5CvTzf8ZpX9x5nRe9W2bAr', 360306),
        ('A Day In The Life', '5FBf12F4ry9TXoZAvISu6F', 349906),
        ('Dusk Baby', '41Zg0UrERyaxpOWVGohvz3', 339093),
        ('Fascinating Rhythm', '7yzATHuBK563ZDjNPjJ7Yt', 272287),
        ('Crazy Race', '4XyKqXYeL0FBPFbDrXLvJZ', 143280),
        ('4 A.M.', '6HFhLv0wa8129Y7AXgnQC7', 321000),
        ('Marseille (feat. Abd Al Malik)', '6RkGrUeBntd8PSKBdLlt7q', 443480),
        ('Gentle Thoughts', '0PccCPDXV2C1QBgfJyLi9R', 422453),
        ('Summer In The City', '39eFFeKv7QaTBIukk7TYVu', 244440),
        ('Poinciana', '4lyupu0V7V9CoKhH52sfS8', 273760),
        ('Judas', '4qweq7Zp2QnST0lC9WchKA', 249520),
        ('The Dude', '0YeMZY4x8FbVIvFmaphMp6', 337600),
        ('For Once In My Life', '4kP69y3GKHi9tXckfgp4bK', 169800),
        ('Everybody Needs Somebody (I Need You)', '2vXJCf9IjnzVvpjauiP3Vr', 157186),
        ('Funky Duck', '2KRQR1VK6OoJxpwVzwDv72', 130770),
        ('Bach Vision Test', '2UTm8CgM1SNpslEQGzpsmW', 149505),
        ('I Was Made To Love Her', '2aCKBrLn7rbhStk5k4FwnF', 156440),
        ('Junjo', '4NmvKXxRdHwCSUllXlG7md', 313506),
        ('Cuerpo Y Alma', '2gTIfTr9XOv7Brek0785J9', 481080),
        ('Fall In', '6k0lzN7Kxib0afD6cgPHsG', 236786),
        ('Fall In', '6k0lzN7Kxib0afD6cgPHsG', 236786),
        ('It Never Entered My Mind', '6QlkHjQmo2YncQN5MQXgPZ', 323186),
        ('Can We Pretend', '0S5ZoKKZD3bllkvhEoPimZ', 229573),
        ('Below The Valleys', '32Kg7L3mgzcekEo7z9pypH', 181000),
        ('Gibraltar', '2Ji6pcpNIuRPSilgKHjnN6', 232986),
        ('Have You Met Miss Jones?', '2Ob1A4itFyJWUa6fpwqAOs', 253840),
        ('The Well-Tempered Clavier, Book 1: Fugue No. 1 in C Major, BWV 846', '0dpy8R09X1a0UN8NNE8RYI', 116933),
        ('Gibraltar', '2Ji6pcpNIuRPSilgKHjnN6', 232986),
        ('Wait for the Moment', '48wH8bAxvBJO2l14GmNLz7', 230676),
        ('Symphony No.3 in E flat, Op.55 -"Eroica": 3. Scherzo (Allegro vivace)', '0orbWbXHJbAkYq2l2B3L9g', 332666),
        ('15 Piano Variations and Fugue in E flat, Op.35 -"Eroica Variations": Variation 3', '1dOxSeuf550LvHq9RrMrWd',40000),
        ('Shostakovich: Fugue No. 7 In A Major', '4ZIYqwSH9aQj0Ua3jnhZsf', 163386),
        ('Partita for 8 Singers: No. 1. Allemande', '6SKsopY3khZl3BcqGlxoMB', 353466),
        ('I Want You Back', '5LxvwujISqiB8vpRYv887S', 176333)
    ]

    w = [t[2] for t in tracks]
    W = target*60*1000

    I = range(len(w))
    m = Model('targetsum')
    x = [m.add_var(var_type=BINARY) for i in I]
    m.objective = minimize(xsum(x[i]*w[i] for i in I) - W)
    m += (xsum(x[i]*w[i] for i in I) - W) >= 0

    m.optimize()

    selected = [i for i in I if x[i].x>=0.99]

    print([t for i, t in enumerate(tracks) if i in selected])
    print(sum(t[2] for i, t in enumerate(tracks) if i in selected)/60000)
    print(m.objective_value)
    print('{:2.2f}%'.format(100*m.objective_value/W))