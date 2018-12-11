def _profile_func(func):
    import cProfile
    import time
    cp = cProfile.Profile()
    cp.enable()
    start_time = time.time()

    func()

    cp.disable()
    cp.print_stats()
    print("--- %s seconds ---" % (time.time() - start_time))