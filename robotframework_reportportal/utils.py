def get_list_as_str(l):
    if l:
        r = l[0]
        for i in range(1, len(l)):
            r += ", {0}".format(l[i])
        return r
    else:
        return ""
