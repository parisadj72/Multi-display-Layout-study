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
}
