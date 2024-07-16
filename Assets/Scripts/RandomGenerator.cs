using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RandomGenerator : MonoBehaviour
{
    public static List<int> randomizeList(int size)
    {
        List<int> randomList = new List<int>();
        //randomList.Add(UnityEngine.Random.Range(0, size));

        while (randomList.Count < size)
        {
            int randomLayout = UnityEngine.Random.Range(0, size);
            if (randomList.Contains(randomLayout))
            {
                continue;
            }
            else randomList.Add(randomLayout);
        }
        return randomList;
    }
    public static List<int> shuffleList(List<int> list)
    {
        List<int> list2 = new List<int>();
        List<int> indexList = new List<int>();

        while (indexList.Count != list.Count)
        {
            int rand = UnityEngine.Random.Range(0, list.Count);
            if (indexList.Contains(rand))
                continue;
            else
            {
                list2.Add(list[rand]);
                indexList.Add(rand);
            }
        }
        return list2;
    }
}
