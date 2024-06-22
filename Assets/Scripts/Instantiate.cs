using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Instantiate : MonoBehaviour
{
    public GameObject layoutPrefab;
    private void Awake()
    {
        
        Instantiate(layoutPrefab, new Vector3(0,0,0), Quaternion.identity);
    }
}
